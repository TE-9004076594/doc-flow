## MODIFIED Requirements

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

#### Scenario: Reject invalid file format
- **WHEN** user selects or drops a non-`.docx` file (e.g., `.pdf`, `.png`)
- **THEN** the system SHALL display a clear error message indicating only `.docx` files are supported
- **AND** the upload button SHALL remain disabled

#### Scenario: Reject oversized file
- **WHEN** user selects a file exceeding 50MB
- **THEN** the system SHALL display an error message indicating the size limit

#### Scenario: Show upload progress
- **WHEN** file upload is in progress
- **THEN** the system SHALL display a progress bar showing upload percentage
- **AND** the upload button SHALL be disabled during upload

## ADDED Requirements

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
