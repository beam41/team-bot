from constants import MAX_POSITIONS

# ===== ENVIRONMENT VARIABLES =====
DISCORD_TOKEN_ENV = 'DISCORD_TOKEN'
TEAM_THREAD_PARENT_ID_ENV = 'TEAM_THREAD_PARENT_ID'

# ===== VALIDATION PATTERNS =====
HEX_COLOR_PATTERN = r'^[0-9A-F]{6}$'
TEAM_TAG_PATTERN = r'^[A-Z0-9]{2,6}$'

# ===== TEAM COMMAND GROUP =====
TEAM_CMD_GROUP = "team"
TEAM_CMD_GROUP_DESC = "Team commands"

# ===== REGISTER TEAM COMMAND =====
REGISTER_TEAM_CMD = "register"
REGISTER_TEAM_CMD_DESC = "Register a team, use this under your team threads [OWNER/ADMIN ONLY]"
REGISTER_TEAM_CMD_NAME_DESC = "Team name"
REGISTER_TEAM_CMD_TAG_DESC = "Team tag"
REGISTER_TEAM_CMD_TEAM_COLOR_DESC = "Team official color (used in role)"
REGISTER_TEAM_CMD_AUTO_ACCEPT_DESC = "Auto accept team members, aka FFA team"
REGISTER_TEAM_CMD_REASON_PLACEHOLDER_DESC = "Placeholder for the reason input, this will be used on join request pop up"
REGISTER_TEAM_CMD_SKIP_MAKE_ROLE_DESC = "For legacy team, ask admin to link role to the team"
REGISTER_TEAM_CMD_POSITION_DESC = f"List of positions for the team members to select, separated by commas (e.g., 'Driver, Navigator, Engineer') max {MAX_POSITIONS}"

# ===== UNREGISTER TEAM COMMAND =====
UNREGISTER_TEAM_CMD = "unregister"
UNREGISTER_TEAM_CMD_DESC = "Unregister a team, warn: this will delete the teams data and role if exists! [OWNER/ADMIN ONLY]"

# ===== TEAM DETAILS COMMAND =====
TEAM_DETAILS_CMD = "details"
TEAM_DETAILS_CMD_DESC = "View details of a team registered in this thread"

# ===== JOIN TEAM COMMAND =====
JOIN_TEAM_CMD = "join_team"
JOIN_TEAM_CMD_DESC = "Join a team registered in this thread, join request will be posted if team is not auto accept"

# ===== LEAVE TEAM COMMAND =====
LEAVE_TEAM_CMD = "leave_team"
LEAVE_TEAM_CMD_DESC = "Leave a team registered in this thread, this will not notify anyone don't worry"

# ===== TEAM MEMBER COMMAND =====
TEAM_MEMBER_CMD_GROUP = "team_member"
TEAM_MEMBER_CMD_GROUP_DESC = "Manage team members [OWNER/ADMIN ONLY]"
ADD_TEAM_MEMBER_CMD = "add"
ADD_TEAM_MEMBER_CMD_DESC = "Add a member to team registered in this thread [OWNER/ADMIN ONLY]"
REMOVE_TEAM_MEMBER_CMD = "remove"
REMOVE_TEAM_MEMBER_CMD_DESC = "Remove a member from team registered in this thread, silently [OWNER/ADMIN ONLY]"

# ===== UPDATE MEMBER COMMAND GROUP =====
UPDATE_MEMBER_INFO_CMD_GROUP = "update"
UPDATE_MEMBER_INFO_CMD_GROUP_DESC = "Update team member information"

# ===== CHANGE PLAYER NUMBER COMMAND =====
CHANGE_PLAYER_NUMBER_CMD = "number"
CHANGE_PLAYER_NUMBER_CMD_DESC = "Change a player's number in the team"
CHANGE_PLAYER_NUMBER_CMD_NEW_NUMBER_DESC = "New player number to update to, must be between 0 and 99"
CHANGE_PLAYER_NUMBER_CMD_MEMBER_DESC = "Leave blank to update yourself, owner/admin can change team member number"

# ===== CHANGE POSITION COMMAND =====
CHANGE_POSITION_CMD = "position"
CHANGE_POSITION_CMD_DESC = "Change a player's position in the team"
CHANGE_POSITION_CMD_POSITION_DESC = "Position name to assign to the player"
CHANGE_POSITION_CMD_MEMBER_DESC = "Leave blank to update yourself, owner/admin can change team member position"
TEAM_OWNER_OR_ADMIN_CHANGE_POSITION_ERR = "Only the team owner or server administrators can change other players' positions"
PLAYER_POSITION_CHANGED_TITLE = "Position Changed"
PLAYER_POSITION_CHANGED_DESC = "<@{}>'s position was changed from {} to {} in team {} [{}]"

# ===== UPDATE TEAM COMMAND GROUP =====
UPDATE_TEAM_CMD_GROUP = "team_update"
UPDATE_TEAM_CMD_GROUP_DESC = "Update a team [OWNER/ADMIN ONLY]"
UPDATE_TEAM_NAME_CMD = "name"
UPDATE_TEAM_NAME_CMD_DESC = "Update the team name [OWNER/ADMIN ONLY]"
UPDATE_TEAM_TAG_CMD = "tag"
UPDATE_TEAM_TAG_CMD_DESC = "Update the team tag [OWNER/ADMIN ONLY]"
UPDATE_TEAM_COLOR_CMD = "color"
UPDATE_TEAM_COLOR_CMD_DESC = "Update the team color [OWNER/ADMIN ONLY]"
UPDATE_TEAM_OWNER_CMD = "owner"
UPDATE_TEAM_OWNER_CMD_DESC = "Update the team owner [OWNER/ADMIN ONLY]"
UPDATE_TEAM_AUTO_ACCEPT_CMD = "auto_accept"
UPDATE_TEAM_AUTO_ACCEPT_CMD_DESC = "Update the team auto_accept [OWNER/ADMIN ONLY]"
UPDATE_TEAM_REASON_CMD = "reason_placeholder"
UPDATE_TEAM_REASON_CMD_DESC = "Update the team join request reason placeholder [OWNER/ADMIN ONLY]"
UPDATE_TEAM_ROLE_CMD = "role"
UPDATE_TEAM_ROLE_CMD_DESC = "Update the team role (only work when there is no role assigned) [ADMIN ONLY]"

# ===== POSITION MANAGEMENT COMMANDS =====
UPDATE_POSITION_CMD_GROUP_DESC = "Update the team positions [OWNER/ADMIN ONLY]"
ADD_POSITION_CMD = "add"
ADD_POSITION_CMD_DESC = "Add a new position to the team [OWNER/ADMIN ONLY]"
ADD_POSITION_CMD_POSITION_DESC = "The name of the position to add"

EDIT_POSITION_CMD = "edit"
EDIT_POSITION_CMD_DESC = "Edit an existing position name [OWNER/ADMIN ONLY]"
EDIT_POSITION_CMD_POSITION_DESC = "The current position name to change"
EDIT_POSITION_CMD_NEW_POSITION_DESC = "The new position name"

DELETE_POSITION_CMD = "delete"
DELETE_POSITION_CMD_DESC = "Delete a position from the team [OWNER/ADMIN ONLY]"
DELETE_POSITION_CMD_POSITION_DESC = "The position name to delete"

# ===== GENERAL ERROR MESSAGES =====
GUILD_ONLY_ERR = "This command can only be used in a guild."
MEMBERS_ONLY_ERR = "This command can only be used by members of the guild."
TEAM_THREADS_ONLY_ERR = "This command can only be used in team threads."

# ===== PERMISSION ERROR MESSAGES =====
THREAD_OWNER_OR_ADMIN_ERR = "You must be the thread owner or administrator to register a team."
TEAM_OWNER_OR_ADMIN_ERR = "You must be the team owner or an administrator to unregister a team."
TEAM_OWNER_OR_ADMIN_UPDATE_ERR = "You must be the team owner or an administrator to update a team."
ADMIN_ONLY_UPDATE_ERR = "You must an administrator to update a team."
TEAM_OWNER_OR_ADMIN_ACCEPT_ERR = "You must be the team owner or an administrator to accept a join request."
TEAM_OWNER_OR_ADMIN_REJECT_ERR = "You must be the team owner or an administrator to reject a join request."
TEAM_OWNER_OR_ADMIN_ADD_ERR = "You must be the team owner or an administrator to add members."
TEAM_OWNER_OR_ADMIN_REMOVE_ERR = "You must be the team owner or an administrator to remove members."
TEAM_OWNER_OR_ADMIN_CHANGE_NUMBER_ERR = "You must be the team owner or an administrator to change player numbers."
TEAM_OWNER_OR_ADMIN_POSITION_ERR = "You must be the team owner or an administrator to manage positions."

# ===== VALIDATION ERROR MESSAGES =====
INVALID_COLOR_ERR = "Invalid team color. Valid colors are #<3 or 6 hexadecimal digits>, rgb(<number>, <number>, <number>), or color names like 'blue', 'red', etc."
INVALID_TAG_ERR = "Invalid team tag. Please provide a valid tag (2-6 uppercase letters or numbers)."
PLAYER_NUMBER_RANGE_ERR = "Player number must be between 0 and 99."
PLAYER_NUMBER_INVALID_ERR = "Player number must be a valid number between 0 and 99."
TOO_MANY_POSITIONS_ERR = f"Too many positions specified. Maximum allowed is {MAX_POSITIONS}."
MAX_POSITIONS_ERR = f"Max positions reached. Maximum allowed is {MAX_POSITIONS}."

# ===== POSITION ERROR MESSAGES =====
POSITION_ALREADY_EXISTS_ERR = "A position with that name already exists."
POSITION_NOT_FOUND_ERR = "No position found with that name."
POSITION_NAME_EMPTY_ERR = "Position name cannot be empty."

# ===== TEAM STATE ERROR MESSAGES =====
TEAM_ALREADY_REGISTERED_ERR = "Team is already registered in this thread."
TEAM_NAME_OR_TAG_EXISTS_ERR = "Team is already registered with the same name or tag."
TEAM_NAME_EXISTS_ERR = "Team is already registered with the same name."
TEAM_TAG_EXISTS_ERR = "Team is already registered with the same tag."
NO_TEAM_REGISTERED_ERR = "No team registered in this thread."

# ===== MEMBER STATE ERROR MESSAGES =====
ALREADY_TEAM_MEMBER_ERR = "You are already a member of this team."
USER_ALREADY_MEMBER_ERR = "User is already a member of this team."
NOT_TEAM_MEMBER_ERR = "You are not a member of this team."
USER_NOT_MEMBER_ERR = "User is not a member of this team."
OWNER_CANNOT_LEAVE_ERR = "You cannot leave the team as the owner. Please transfer ownership or unregister the team."
CANNOT_REMOVE_OWNER_ERR = "You cannot remove the team owner."
CANNOT_ADD_BOT_ERR = "You cannot add a bot as a team member."
CANNOT_SET_BOT_OWNER_ERR = "You cannot set a bot as the team owner."
OWNER_NOT_MEMBER_ERR = "The specified user is not a member of the team."

# ===== ROLE OPERATION ERROR MESSAGES =====
ROLE_UPDATE_WITH_EXISTING_ERR = "You cannot update the role if the team already has a role assigned, update tag and color instead."

# ===== ROLE OPERATION ERROR EMBEDS =====
ROLE_CREATION_FAILED_TITLE = "Role Creation Failed"
ROLE_CREATION_FAILED_DESC_PERMISSION = "I do not have permission to create roles in this guild, please ask admin to create manually."
ROLE_CREATION_FAILED_DESC_FAILED = "Failed to create role: {}, please ask admin to create manually."

ROLE_ASSIGNMENT_FAILED_TITLE = "Role Assignment Failed"
ROLE_ASSIGNMENT_FAILED_DESC_PERMISSION = "I do not have permission to assign roles in this guild."
ROLE_ASSIGNMENT_FAILED_DESC_FAILED = "Failed to assign role: {}"

ROLE_REMOVAL_FAILED_TITLE = "Role Removal Failed"
ROLE_REMOVAL_FAILED_DESC_PERMISSION = "I do not have permission to unassign roles in this guild."
ROLE_REMOVAL_FAILED_DESC_FAILED = "Failed to unassign role: {}"

ROLE_DELETION_FAILED_TITLE = "Role Deletion Failed"
ROLE_DELETION_FAILED_DESC_PERMISSION = "I do not have permission to delete roles in this guild, please ask admin to delete manually."
ROLE_DELETION_FAILED_DESC_FAILED = "Failed to delete role: {}, please ask admin to delete manually."

ROLE_UPDATE_FAILED_TITLE = "Role Update Failed"
ROLE_UPDATE_FAILED_DESC = "Failed to update role: {}"

# ===== TEAM REGISTRATION EMBED =====
TEAM_REGISTERED_TITLE = "Team Registered"
TEAM_REGISTERED_DESC = "Team **{}** **[{}]** has been registered successfully."
TEAM_REGISTERED_FIELD_OWNER = "Owner"
TEAM_REGISTERED_FIELD_ROLE = "Role"
TEAM_REGISTERED_FIELD_TEAM_COLOR = "Team Color"
TEAM_REGISTERED_FIELD_AUTO_ACCEPT = "Auto Accept"

# ===== TEAM UNREGISTRATION EMBED =====
TEAM_UNREGISTERED_TITLE = "Team Unregistered"
TEAM_UNREGISTERED_DESC = "Team **{}** **[{}]** has been unregistered successfully."
UNREGISTRATION_CANCELLED_TITLE = "Unregistration Cancelled"
UNREGISTRATION_CANCELLED_DESC = "You have cancelled the unregistration."
UNREGISTER_TEAM_CONFIRMATION_TITLE = "Unregister Team Confirmation"
UNREGISTER_TEAM_CONFIRMATION_DESC = "Are you sure you want to unregister this team? This action cannot be undone."

# ===== TEAM DETAILS EMBED =====
TEAM_DETAILS_TITLE = "Team Details"
TEAM_DETAILS_DESC = "Team **{}** **[{}]**"
TEAM_DETAILS_FIELD_MEMBERS = "Members"
TEAM_DETAILS_FIELD_OWNER = "Owner"
TEAM_DETAILS_FIELD_ROLE = "Role"
TEAM_DETAILS_FIELD_TEAM_COLOR = "Team Color"
TEAM_DETAILS_FIELD_AUTO_ACCEPT = "Auto Accept"
TEAM_DETAILS_FIELD_AVAILABLE_POSITIONS = "Available Positions"

# ===== TEAM LEFT EMBED =====
TEAM_LEFT_TITLE = "Team left"
TEAM_LEFT_DESC = "You have successfully leave the team **{}** **[{}]**."

# ===== TEAM JOINED EMBED =====
TEAM_JOINED_TITLE = "Team Joined"
TEAM_JOINED_DESC = "**{} (IGN: {})** have successfully join the team **{}** **[{}]** with number **`{:02d}`**, welcome to the team!"
TEAM_JOINED_FIELD_REASON = "Reason"
TEAM_JOINED_FIELD_MEMBERS = "Members"

# ===== TEAM MEMBER ADDED EMBED =====
TEAM_MEMBER_ADDED_TITLE = "Team Member Added"
TEAM_MEMBER_ADDED_DESC = "<@{}> has been added to team **{}** **[{}]** with number **`{:02d}`**{}."
TEAM_MEMBER_ADDED_FIELD_CURRENT_MEMBERS = "Current Members"

# ===== TEAM MEMBER REMOVED EMBED =====
TEAM_MEMBER_REMOVED_TITLE = "Team Member Removed"
TEAM_MEMBER_REMOVED_DESC = "<@{}> has been removed from team **{}** **[{}]**."
TEAM_MEMBER_REMOVED_FIELD_CURRENT_MEMBERS = "Current Members"

# ===== TEAM UPDATED EMBED =====
TEAM_UPDATED_TITLE = "Team Updated"
TEAM_UPDATED_DESC = "Team **{}**  **[{}]** has been updated successfully."
TEAM_UPDATED_FIELD_OWNER = "Owner"
TEAM_UPDATED_FIELD_ROLE = "Role"
TEAM_UPDATED_FIELD_TEAM_COLOR = "Team Color"
TEAM_UPDATED_FIELD_AUTO_ACCEPT = "Auto Accept"

# ===== PLAYER NUMBER CHANGED EMBED =====
PLAYER_NUMBER_CHANGED_TITLE = "Player Number Changed"
PLAYER_NUMBER_CHANGED_DESC = "<@{}>'s player number has been changed from **`{:02d}`** to **`{:02d}`** in team **{}** **[{}]**."

# ===== POSITION MANAGEMENT EMBEDS =====
POSITION_ADDED_TITLE = "Position Added"
POSITION_ADDED_DESC = "Position **{}** has been added to team **{}** **[{}]**."
POSITION_ADDED_FIELD_CURRENT_POSITIONS = "Current Positions"

POSITION_UPDATED_TITLE = "Position Updated"
POSITION_UPDATED_DESC = "Position **{}** has been renamed to **{}** in team **{}** **[{}]**."
POSITION_UPDATED_FIELD_CURRENT_POSITIONS = "Current Positions"

POSITION_DELETED_TITLE = "Position Deleted"
POSITION_DELETED_DESC = "Position **{}** has been deleted from team **{}** **[{}]**."
POSITION_DELETED_FIELD_CURRENT_POSITIONS = "Current Positions"

# ===== JOIN REQUEST EMBED =====
JOIN_REQUEST_TITLE = "Join Request"
JOIN_REQUEST_DESC = "**{} (IGN: {})** has requested to join the team **{}** **[{}]** with number **`{:02d}`**."
JOIN_REQUEST_FIELD_REASON = "Reason"

# ===== JOIN REQUEST REJECTED EMBED =====
JOIN_REQUEST_REJECTED_TITLE = "Join Request Rejected"
JOIN_REQUEST_REJECTED_DESC = "This join request has been rejected."

# ===== JOIN REQUEST UI MODAL =====
UI_MODAL_TITLE = 'Join request question'
UI_LABEL_IGN = 'In game name'
UI_LABEL_PLAYER_NUMBER = 'Player number (00-99)'
UI_LABEL_REASON = 'Reason'
UI_PLACEHOLDER_PLAYER_NUMBER = 'Enter number 0-99'
UI_PLACEHOLDER_REASON_OPTIONAL = "{} (optional)"
UI_PLACEHOLDER_POSITION = 'Select a position (optional)'

# ===== JOIN REQUEST UI BUTTONS =====
UI_BUTTON_ACCEPT = "Accept"
UI_BUTTON_REJECT = "Reject"
UI_NOTE_OWNER_ONLY = "Note: only the team owner can accept or reject this request."

# ===== SHARED FORMATTING STRINGS =====
FORMAT_TEAM_MEMBER = "**`{:02d}`** <@{}>{}"
FORMAT_TEAM_COLOR_DISPLAY = "`#{}`"
FORMAT_USER_MENTION = "<@{}>"
FORMAT_ROLE_MENTION = "<@&{}>"
FORMAT_LOGGED_IN = 'We have logged in as {}'
FORMAT_SYNCED_COMMANDS = 'Synced {} commands'
FORMAT_POS = " - {}"
FORMAT_POS_AS = " AS **{}**"
# ===== SHARED DISPLAY VALUES =====
BOOL_YES = "Yes"
BOOL_NO = "No"
ROLE_NO_ROLE = "No role"
ROLE_NO_ROLE_CREATED = "No role created"
POSITIONS_NO_POSITIONS = "No positions available"
AS = "as"

# ===== ENVIRONMENT ERROR MESSAGES =====
DISCORD_TOKEN_ERR = "DISCORD_TOKEN must be set in the environment variables."
TEAM_THREAD_PARENT_ID_ERR = "TEAM_THREAD_PARENT_ID must be set and must be a valid integer."
