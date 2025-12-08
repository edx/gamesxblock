# Games XBlock API Documentation

This document describes the APIs available in the Games XBlock for implementing gamification features in Open edX courses. The XBlock supports two game types: **Flashcards** and **Matching**.

## Table of Contents

- [XBlock Fields](#xblock-fields)
- [Common APIs](#common-apis)
- [Flashcards Game APIs](#flashcards-game-apis)
- [Matching Game APIs](#matching-game-apis)
- [Data Structures](#data-structures)

---

## XBlock Fields

The Games XBlock uses the following fields to store configuration and state:

### Content-Scoped Fields
- **`title`** (string): The title displayed in the XBlock. Default varies by game type.
- **`cards`** (list): List of card objects containing terms and definitions.
- **`list_length`** (integer): Number of cards in the list (for convenience).

### Settings-Scoped Fields
- **`display_name`** (string): Display name for the XBlock. Default: `"Games XBlock"`.
- **`game_type`** (string): Type of game - either `"flashcards"` or `"matching"`. Default: `"matching"`.
- **`is_shuffled`** (boolean): Whether cards should be shuffled. Default: `true`.
- **`has_timer`** (boolean): Whether the game should display a timer. Default: `true`.

### User State Fields
- **`best_time`** (integer): Best completion time in seconds for matching game (user-specific).

---

## Common APIs

These APIs work across both flashcards and matching game types.

### `get_settings`

**Type**: JSON Handler
**Description**: Retrieves current game configuration including game type, cards, shuffle setting, and timer setting.

**Request**:
```json
{}
```

**Response**:
```json
{
  "game_type": "matching",
  "cards": [
    {
      "term": "Python",
      "term_image": "http://example.com/python.png",
      "definition": "A high-level programming language",
      "definition_image": "",
      "order": 0,
      "card_key": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "is_shuffled": true,
  "has_timer": true
}
```

**Fields**:
- `game_type` (string): Current game type (`"flashcards"` or `"matching"`)
- `cards` (array): List of card objects (see [Card Object](#card-object))
- `is_shuffled` (boolean): Shuffle setting
- `has_timer` (boolean): Timer setting

---

### `save_settings`

**Type**: JSON Handler
**Description**: Saves game type, shuffle setting, timer setting, and all cards in one API call. Validates card format and generates unique identifiers.

**Request**:
```json
{
  "game_type": "flashcards",
  "is_shuffled": true,
  "has_timer": false,
  "display_name": "My Vocabulary Game",
  "cards": [
    {
      "term": "Algorithm",
      "term_image": "",
      "definition": "A step-by-step procedure for solving a problem",
      "definition_image": "http://example.com/algo.png"
    },
    {
      "term": "Data Structure",
      "term_image": "http://example.com/ds.png",
      "definition": "A way of organizing data efficiently",
      "definition_image": ""
    }
  ]
}
```

**Response** (Success):
```json
{
  "success": true,
  "game_type": "flashcards",
  "cards": [
    {
      "term": "Algorithm",
      "term_image": "",
      "definition": "A step-by-step procedure for solving a problem",
      "definition_image": "http://example.com/algo.png",
      "order": 0,
      "card_key": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
    },
    {
      "term": "Data Structure",
      "term_image": "http://example.com/ds.png",
      "definition": "A way of organizing data efficiently",
      "definition_image": "",
      "order": 1,
      "card_key": "3f847e5d-8a6b-4c3e-9d2a-1b8f7c4e0d9a"
    }
  ],
  "count": 2,
  "is_shuffled": true,
  "has_timer": false
}
```

**Response** (Error):
```json
{
  "success": false,
  "error": "Each card must have term and definition"
}
```

**Validation Rules**:
- Each card must be an object/dictionary
- Each card must contain both `term` and `definition` fields
- Missing `card_key` will be auto-generated as UUID
- Missing image URLs default to empty strings

---

### `upload_image`

**Type**: HTTP Handler
**Description**: Uploads an image file to configured storage (S3 or default) and returns the URL.

**Request**:
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - `file` (file): The image file to upload

**Supported Extensions**: jpg, jpeg, png, gif, webp, svg

**Response** (Success):
```json
{
  "success": true,
  "url": "https://s3.amazonaws.com/bucket/games/block_id/abc123def456.png",
  "filename": "my-image.png",
  "file_path": "games/block_id/abc123def456.png"
}
```

**Response** (Error - No Extension):
```json
{
  "success": false,
  "error": "File must have an extension"
}
```

**Response** (Error - Invalid Extension):
```json
{
  "success": false,
  "error": "Unsupported file type '.bmp'. Allowed: gif, jpg, jpeg, png, svg, webp"
}
```

**Notes**:
- File is stored with MD5 hash to prevent duplicates
- File path format: `gamesxblock/<block_id>/<md5_hash>.<ext>`

---

### `delete_image_handler`

**Type**: JSON Handler
**Description**: Deletes an image from storage by its key/path.

**Request**:
```json
{
  "key": "gamesxblock/block_id/abc123def456.png"
}
```

**Response** (Success):
```json
{
  "success": true,
  "key": "gamesxblock/block_id/abc123def456.png"
}
```

**Response** (Error - Missing Key):
```json
{
  "success": false,
  "error": "Missing key"
}
```

**Response** (Error - File Not Found):
```json
{
  "success": false,
  "key": "gamesxblock/block_id/nonexistent.png"
}
```

---

## Flashcards Game APIs

### `student_view` (Flashcards)

**Type**: XBlock View
**Description**: Renders the flashcards game interface for students.

**Features**:
- Displays cards one at a time
- Flip animation to reveal definitions
- Navigate forward/backward through cards
- Optional shuffle on load
- Progress indicator

**Rendered Context**:
```python
{
  "title": "Flashcards",
  "list_length": 10,
  "encoded_mapping": "eyJjYXJkcyI6W3sidGVybSI6...",  # Base64-encoded card data
  "obf_decoder": "function FlashcardsInit(r,e){...}",  # Obfuscated initialization
  "data_element_id": "abc123xyz789"
}
```

**Data Payload Structure** (decoded from `encoded_mapping`):
```json
{
  "cards": [
    {
      "id": "card-uuid",
      "term": "Front text",
      "definition": "Back text",
      "term_image": "http://example.com/front.png",
      "definition_image": "http://example.com/back.png"
    }
  ],
  "salt": "randomString123"
}
```

---

## Matching Game APIs

### `student_view` (Matching)

**Type**: XBlock View
**Description**: Renders the matching game interface for students where they match terms with definitions.

**Features**:
- Two-column layout (terms on left, definitions on right)
- Click to match pairs
- Optional timer to track completion time
- Multi-page support for large card sets (6 matches per page by default)
- Confetti animation on completion
- Best time tracking

**Rendered Context**:
```python
{
  "title": "Matching Game",
  "list_length": 12,
  "all_pages": [
    {
      "left_items": [{"text": "Python", "index": 0}, ...],
      "right_items": [{"text": "Programming language", "index": 1}, ...]
    }
  ],
  "has_timer": true,
  "total_pages": 2,
  "encoded_mapping": "eyJrZXkiOiJnQUFBQUFBQUFBQUE...",
  "obf_decoder": "function MatchingInit(r,e){...}",
  "data_element_id": "xyz789abc123"
}
```

**Data Payload Structure** (decoded from `encoded_mapping`):
```json
{
  "key": "gAAAAABh...encrypted_mapping_data",
  "pages": [
    {
      "left_items": [
        {"text": "Python", "index": 0},
        {"text": "JavaScript", "index": 2}
      ],
      "right_items": [
        {"text": "Programming language", "index": 1},
        {"text": "Web scripting", "index": 3}
      ]
    }
  ]
}
```

**Security Note**: The matching key mapping is encrypted using Fernet symmetric encryption with a key derived from the block ID and a salt.

---

### `start_matching_game`

**Type**: JSON Handler
**Description**: Decrypts and returns the key mapping for matching game validation. Called when game starts to enable client-side match validation.

**Request**:
```json
{
  "matching_key": "gAAAAABh3k2J..."
}
```

**Response** (Success):
```json
{
  "success": true,
  "data": [
    "550e8400-e29b-41d4-a716-446655440001",
    "3f847e5d-8a6b-4c3e-9d2a-1b8f7c4e0d02",
    null,
    null
  ]
}
```

**Response** (Error - Missing Key):
```json
{
  "success": false,
  "error": "Missing matching_key parameter"
}
```

**Response** (Error - Decryption Failed):
```json
{
  "success": false,
  "error": "Failed to decrypt mapping: Invalid token"
}
```

**Notes**:
- The `data` array contains UUID-like strings representing valid matches
- Each index maps to its matching pair's index
- Encryption prevents students from easily discovering correct matches

---

### `complete_matching_game`

**Type**: JSON Handler
**Description**: Records completion time and updates the user's best time if the new time is better.

**Request**:
```json
{
  "new_time": 45
}
```

**Response**:
```json
{
  "new_time": 45,
  "prev_best_time": 52
}
```

**Response** (First Completion):
```json
{
  "new_time": 67,
  "prev_best_time": null
}
```

**Fields**:
- `new_time` (integer): Completion time in seconds for this attempt
- `prev_best_time` (integer|null): Previous best time, or `null` if first completion

**Behavior**:
- If `new_time < prev_best_time`, updates `best_time` field
- If `prev_best_time` is `null`, sets `best_time` to `new_time`

---

### `refresh_game`

**Type**: HTTP Handler
**Description**: Re-renders the matching game view with newly shuffled cards (if shuffle is enabled).

**Request**:
- **Method**: GET or POST
- **Parameters**: None

**Response**:
- **Content-Type**: text/html; charset=UTF-8
- **Body**: Full HTML fragment of the matching game with new shuffle

**Use Case**: Called when student wants to retry the game with different arrangement.

---

## Data Structures

### Card Object

Represents a single term-definition pair in the game.

```json
{
  "term": "Algorithm",
  "term_image": "http://example.com/algo.png",
  "definition": "A step-by-step procedure for solving a problem",
  "definition_image": "http://example.com/algo-diagram.png",
  "order": 0,
  "card_key": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

**Fields**:
- **`term`** (string, required): The term/question/front side text
- **`term_image`** (string, optional): URL to image for the term
- **`definition`** (string, required): The definition/answer/back side text
- **`definition_image`** (string, optional): URL to image for the definition
- **`order`** (integer, optional): Display order (auto-generated if missing)
- **`card_key`** (string, optional): Unique identifier (auto-generated as UUID if missing)

---

### Item Object (Matching Game)

Represents a draggable/clickable item in the matching game interface.

```json
{
  "text": "Python",
  "index": 0
}
```

**Fields**:
- **`text`** (string): Display text for the item
- **`index`** (integer): Unique index used for match validation

---

### Page Object (Matching Game)

Represents one page of matches in a multi-page matching game.

```json
{
  "left_items": [
    {"text": "Python", "index": 0},
    {"text": "JavaScript", "index": 2}
  ],
  "right_items": [
    {"text": "Programming language", "index": 1},
    {"text": "Web scripting", "index": 3}
  ]
}
```

**Fields**:
- **`left_items`** (array): List of item objects for the left column (terms)
- **`right_items`** (array): List of item objects for the right column (definitions)

**Configuration**: Default is 6 matches per page (configurable via `CONFIG.MATCHES_PER_PAGE`).

---

## Error Handling

All JSON handlers return a consistent error format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common error scenarios:
- Missing required parameters
- Invalid data format
- Encryption/decryption failures
- File upload issues (invalid extension, file too large, etc.)
- Storage backend errors

---

## Security Features

### Encryption
- Matching game uses Fernet symmetric encryption for key mapping
- Encryption key derived from block ID and salt (consistent across requests)
- Prevents students from easily discovering correct matches

### Obfuscation
- JavaScript initialization functions use randomized variable names
- Data embedded in DOM with random element IDs
- Payload encoded in Base64 before embedding
- Makes it harder to reverse-engineer game logic

### Validation
- Server-side validation of card structure
- File extension whitelist for uploads
- MD5 hashing prevents duplicate uploads
- Storage key validation before deletion

---

## Configuration Constants

Key configuration values (from `games/constants.py`):

- **`MATCHES_PER_PAGE`**: 6 - Number of term-definition pairs per page in matching game
- **`RANDOM_STRING_LENGTH`**: 16 - Length of random keys for obfuscation
- **`SALT_LENGTH`**: 12 - Length of salt for payload obfuscation
- **`ENCRYPTION_SALT`**: Internal salt for key generation
- **`PATH_PREFIX`**: "gamesxblock" - Prefix for uploaded file paths

---

## Usage Examples

### Example 1: Create a Flashcards Game

```python
# 1. Save settings with flashcards type
response = xblock.save_settings({
    "game_type": "flashcards",
    "is_shuffled": true,
    "has_timer": false,
    "display_name": "Spanish Vocabulary",
    "cards": [
        {
            "term": "Hola",
            "definition": "Hello"
        },
        {
            "term": "Adiós",
            "definition": "Goodbye"
        }
    ]
})

# 2. Upload images for cards (if needed)
# POST to upload_image handler with multipart/form-data

# 3. Students view the flashcards via student_view
# They can flip cards, navigate, and study terms
```

### Example 2: Create a Matching Game with Timer

```python
# 1. Save settings with matching type
response = xblock.save_settings({
    "game_type": "matching",
    "is_shuffled": true,
    "has_timer": true,
    "display_name": "Computer Science Terms",
    "cards": [
        {
            "term": "Algorithm",
            "definition": "Step-by-step procedure"
        },
        {
            "term": "Variable",
            "definition": "Named storage location"
        },
        {
            "term": "Loop",
            "definition": "Repeated execution"
        }
    ]
})

# 2. Students play the matching game
# - Game loads encrypted key mapping
# - Timer starts when first match is made
# - On completion, time is submitted to complete_matching_game
# - Best time is tracked per user
```

### Example 3: Upload and Use Images

```javascript
// Frontend: Upload image file
const formData = new FormData();
formData.append('file', imageFile);

fetch(uploadImageUrl, {
    method: 'POST',
    body: formData
}).then(response => response.json())
  .then(data => {
      if (data.success) {
          // Use data.url in card definition
          const card = {
              term: "Python Logo",
              term_image: data.url,
              definition: "High-level programming language",
              definition_image: ""
          };
      }
  });
```

---

## Internationalization (i18n)

The Games XBlock supports multiple languages:

- **Default**: English (en)
- **Supported**: Spanish (es_419)
- All user-facing strings are translatable using Django's translation framework
- Use `gettext()` or `gettext_lazy()` for runtime translation
- Translation files located in `games/locale/`
