## ADDED Requirements

### Requirement: User can upload Word templates
The system SHALL allow users to upload `.docx` files as templates. Uploaded templates MUST be parsed to extract structure information, variables, and formatting. The upload MUST be triggered via a frontend modal with drag-and-drop support.

#### Scenario: Open upload modal from template list
- **WHEN** user clicks "上传模板" button on the template list page
- **THEN** an upload modal SHALL open showing a drag-and-drop area and a file selector button

#### Scenario: Select file via drag-and-drop
- **WHEN** user drags a `.docx` file onto the upload area
- **THEN** the file SHALL be accepted and displayed with filename before upload begins

#### Scenario: Select file via file picker
- **WHEN** user clicks the file selector button and chooses a `.docx` file
- **THEN** the file SHALL be accepted and displayed with filename before upload begins

#### Scenario: Successful template upload
- **WHEN** user uploads a valid `.docx` file with template configuration (name, category, description)
- **THEN** the system SHALL store the file, parse its structure, extract `{{variable}}` placeholders, and return a success response with parsed metadata

#### Scenario: Upload invalid file format
- **WHEN** user uploads a non-`.docx` file (e.g., `.pdf`, `.png`)
- **THEN** the system SHALL reject the upload and return a clear error message indicating supported formats

#### Scenario: Upload file size exceeds limit
- **WHEN** user uploads a template file exceeding 50MB
- **THEN** the system SHALL reject the upload and return an error with the maximum allowed size

#### Scenario: Show upload progress
- **WHEN** file upload is in progress
- **THEN** the system SHALL display a progress bar showing upload percentage

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

### Requirement: Upload flow includes metadata form step
After successful file upload, the system SHALL display a metadata form for the user to configure template information before final creation.

#### Scenario: Show metadata form after upload
- **WHEN** file upload completes successfully
- **THEN** the modal SHALL transition to a form with fields: template name (required), description, category (dropdown), tags (tag input)

#### Scenario: Validate required fields
- **WHEN** user clicks "创建" without filling the template name
- **THEN** the system SHALL display a validation error on the name field
- **AND** prevent submission

#### Scenario: Submit and create template
- **WHEN** user fills all required fields and clicks "创建"
- **THEN** the system SHALL send the metadata to the `POST /api/templates` endpoint
- **AND** display a success state with template summary

### Requirement: Upload result shows template summary
After successful template creation, the system SHALL display a result summary before closing the modal.

#### Scenario: Show template creation result
- **WHEN** template is created successfully
- **THEN** the modal SHALL show: template name, detected variable count, template status
- **AND** provide a "查看模板" button linking to the template detail page
- **AND** provide a "关闭" button to return to template list

#### Scenario: Handle upload errors
- **WHEN** template upload or creation fails (network error, server error)
- **THEN** the system SHALL display the error message prominently in the modal
- **AND** allow the user to retry