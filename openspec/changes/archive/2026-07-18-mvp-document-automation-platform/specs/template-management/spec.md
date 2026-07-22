## ADDED Requirements

### Requirement: User can upload Word templates
The system SHALL allow users to upload `.docx` files as templates. Uploaded templates MUST be parsed to extract structure information, variables, and formatting.

#### Scenario: Successful template upload
- **WHEN** user uploads a valid `.docx` file with template configuration (name, category, description)
- **THEN** the system SHALL store the file, parse its structure, extract `{{variable}}` placeholders, and return a success response with parsed metadata

#### Scenario: Upload invalid file format
- **WHEN** user uploads a non-`.docx` file (e.g., `.pdf`, `.png`)
- **THEN** the system SHALL reject the upload and return a clear error message indicating supported formats

#### Scenario: Upload file size exceeds limit
- **WHEN** user uploads a template file exceeding 50MB
- **THEN** the system SHALL reject the upload and return an error with the maximum allowed size

### Requirement: Template supports category and tag classification
The system SHALL allow templates to be organized by department category and business scenario tags for easy retrieval.

#### Scenario: Assign category and tags during upload
- **WHEN** user uploads a template with a department category (e.g., "HR", "Legal") and tags (e.g., "contract", "offer")
- **THEN** the system SHALL save the category and tags and enable retrieval by these attributes

#### Scenario: Filter templates by category
- **WHEN** user browses templates and selects a category filter
- **THEN** the system SHALL display only templates belonging to that category

### Requirement: Template version management
The system SHALL track version history for each template, including version number, update timestamp, change description, and support rollback.

#### Scenario: Create new version on update
- **WHEN** user uploads a new file for an existing template with an update description
- **THEN** the system SHALL create a new version, auto-increment the version number, record the timestamp, and preserve all previous versions

#### Scenario: Compare template versions
- **WHEN** user selects two versions of the same template
- **THEN** the system SHALL display a side-by-side comparison highlighting structural differences

#### Scenario: Rollback to previous version
- **WHEN** user initiates a rollback to a previous template version
- **THEN** the system SHALL restore the selected version as the active version and create a new version entry recording the rollback

### Requirement: Template lifecycle states
The system SHALL support template lifecycle states: draft, pending review, published, and disabled.

#### Scenario: Template starts as draft
- **WHEN** a template is first created
- **THEN** the system SHALL set its status to "draft"
- **AND** only the creator and template admin can view/edit it

#### Scenario: Publish a template
- **WHEN** template admin publishes a template
- **THEN** the system SHALL set its status to "published"
- **AND** all users with view permission can see and use the template

#### Scenario: Disable a published template
- **WHEN** template admin disables a published template
- **THEN** the system SHALL set its status to "disabled"
- **AND** users can no longer use it for document generation
