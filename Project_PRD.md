
---

## Product Requirements Document: Obsidian AI Assistant - Version 1.0

**1. Introduction**

*   **1.1. Product Name:** Obsidian AI Assistant
*   **1.2. Version:** 1.0
*   **1.3. Product Goal:** To create a locally-run AI-powered chat assistant integrated into Obsidian as a plugin. This assistant will be capable of basic conversation and, through the Model Context Protocol (MCP), will perform fundamental interactions with the user's Obsidian vault, such as retrieving note content, creating new notes, and performing simple keyword searches.
*   **1.4. Target Users:** Obsidian users who want to leverage AI to interact with and manage their notes more efficiently. Initially, the primary user is the developer building the plugin.
*   **1.5. Scope for Version 1.0:**
    *   A functional Obsidian plugin providing a chat UI in a side panel.
    *   A local ADK-based Python backend serving the chat logic.
    *   A local Python-based MCP server providing basic tools to interact with the Obsidian vault (read note, create note, keyword search note titles/content).
    *   The ADK backend will use an `MCPToolset` to communicate with the Obsidian MCP Server via stdio.
    *   Basic in-memory session management for conversation context within a single Obsidian session.
*   **1.6. Non-Goals for Version 1.0:**
    *   Nomic embeddings and vector/semantic search for Obsidian notes.
    *   Integration with Gmail, Google Calendar, or any other external MCP servers.
    *   Streaming (SSE) responses from the backend to the plugin (basic request/response for V1).
    *   Persistent session storage across Obsidian restarts.
    *   Advanced error handling or UI polish in the Obsidian plugin beyond basic feedback.
    *   User authentication/authorization for the local backend API itself.
    *   OAuth handling for external services.
    *   Automated process management for starting backend services (user will need to start them manually or via script for V1).
    *   Advanced multi-agent architecture within ADK beyond a single orchestrator using toolsets.

**2. System Architecture (Version 1.0)**

![Architecture Diagram](/public/Architecture.png)

*   **Key Components:** As detailed in the diagram and previous discussions (Obsidian Plugin UI, ADK Agent Backend API, OrchestratorAgent, MCPToolset for Obsidian, Obsidian MCP Server, Obsidian Vault, LLM).

**3. Development Pathway & Detailed Features**

This section outlines the staged development of components and their V1.0 functionalities.

**Stage 1: Backend Foundation - ADK Agent API & Dummy MCP Test**

*   **Goal:** Establish a minimal, working ADK agent backend callable via HTTP, capable of proving MCP interaction with a dummy server.
*   **3.1. Dummy MCP Server (Python/mcp library)**
    *   **REQ-DUMMYMCP-001:** Implemented as `dummy_mcp_echo_server.py`.
    *   **REQ-DUMMYMCP-002:** Communicates via stdio.
    *   **REQ-DUMMYMCP-003 (Tool):** Exposes one tool: `echo_tool(text_to_echo: str)` which returns the input text. Description: "Echoes back the provided text input." Input Schema: `{"type": "object", "properties": {"text_to_echo": {"type": "string"}}, "required": ["text_to_echo"]}`. Output: `{"status": "success", "echoed_text": "input_text_here"}` as part of MCP content.
    *   **REQ-DUMMYMCP-004:** Implements `list_tools` and `call_tool` MCP handlers.
    *   **REQ-DUMMYMCP-005:** Logs startup and tool calls to `stderr`.
*   **3.2. ADK Agent Backend (V1.0a - Python/ADK/FastAPI)**
    *   **REQ-BE-S1-001 (Setup):** Python project structure (`orchestrator_agent_module/agent.py`, `.env`).
    *   **REQ-BE-S1-002 (Agent Definition):** Define `OrchestratorAgent(LlmAgent)`. Instruction: "You are a test assistant. If the user says 'echo [some text]', use the 'echo_tool' with that text." LLM configurable via `.env`.
    *   **REQ-BE-S1-003 (MCP Toolset - Dummy):** Integrate `MCPToolset` with `StdioServerParameters` to run `dummy_mcp_echo_server.py` (path as a constant). `OrchestratorAgent.tools` contains this toolset.
    *   **REQ-BE-S1-004 (Session):** Use `InMemorySessionService`.
    *   **REQ-BE-S1-005 (API):** Run via `adk api_server orchestrator_agent_module`, exposing POST `/run` endpoint.
        *   Accepts: `app_name`, `user_id`, `session_id`, `new_message`.
        *   Returns: JSON array of ADK `Event` objects.
    *   **REQ-BE-S1-006 (Logging):** Basic ADK logs and application-level print statements for API calls and tool decisions.

**Stage 2: Obsidian Plugin UI - Basic Chat Interface**

*   **Goal:** Create the side panel UI in Obsidian and connect it to the Stage 1 ADK Backend for basic text chat and dummy tool interaction.
*   **3.3. Obsidian Plugin UI (V1.0a - TypeScript/Obsidian API)**
    *   **REQ-UI-S2-001 (Side Panel):** Implement `ChatView extends ItemView` with unique type, display text.
    *   **REQ-UI-S2-002 (Activation):** Ribbon icon and command palette entry "ADK Chat: Open Panel".
    *   **REQ-UI-S2-003 (Chat Elements):** Scrollable message history, text input, send button ("Enter" key also sends).
    *   **REQ-UI-S2-004 (Message Display):** Optimistically display user messages. Display agent's final text response from backend events. Clear input field after send. Auto-scroll.
    *   **REQ-UI-S2-005 (Backend Communication):**
        *   On send, POST to `/run` (default `http://localhost:8000/run`, hardcoded V1).
        *   Construct JSON payload: `app_name="orchestrator_agent_module"`, fixed `user_id="obsidian_user_v1"`, plugin-managed `session_id`, `new_message`.
        *   Parse response array of ADK `Event`s, extract final text message (where `is_final_response`).
        *   Display basic network/HTTP errors as agent messages.
    *   **REQ-UI-S2-006 (Session ID):** Generate/store unique `session_id` per Obsidian session (plugin variable).

**Stage 3: Intelligent Obsidian MCP Server & Integration**

*   **Goal:** Replace the Dummy MCP Server with a functional one for basic Obsidian vault interactions.
*   **3.4. Intelligent Obsidian MCP Server (V1.0 - Python/mcp library)**
    *   **REQ-MCP-O-S3-001 (Script):** Implement as `intelligent_obsidian_mcp_server.py`.
    *   **REQ-MCP-O-S3-002 (Stdio):** Communicate via stdio.
    *   **REQ-MCP-O-S3-003 (Vault Path):** Configurable vault path (env var `OBSIDIAN_VAULT_PATH` or dev-time hardcode, documented).
    *   **REQ-MCP-O-S3-004 (Tools - `list_tools`):** Expose:
        *   `get_obsidian_note_content(note_title: str)`: Reads note. Schema: `{"type": "object", "properties": {"note_title": {"type": "string"}}, "required": ["note_title"]}`.
        *   `create_obsidian_note(title: str, content: str)`: Creates note. Schema: `{"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}, "required": ["title", "content"]}`.
        *   `keyword_search_notes(query: str, max_results: int = 3)`: Keyword search. Schema: `{"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 3}}, "required": ["query"]}`.
    *   **REQ-MCP-O-S3-005 (Tool Logic - `call_tool`):**
        *   `get_obsidian_note_content`: Returns `{"status": "success", "content": "note_content_string"}` or error.
        *   `create_obsidian_note`: Returns `{"status": "success", "path": "new_note_path_string"}` or error.
        *   `keyword_search_notes`: Case-insensitive search in `.md` titles/content in vault root. Returns `{"status": "success", "results": [{"title": "str", "path": "str"}]}` or error. (No snippets for V1).
    *   **REQ-MCP-O-S3-006 (Logging):** Log to `stderr`.
*   **3.5. ADK Agent Backend (V1.0b - Update `OrchestratorAgent`)**
    *   **REQ-BE-S3-001 (Update MCPToolset):** `MCPToolset` in `OrchestratorAgent` now runs `intelligent_obsidian_mcp_server.py`.
    *   **REQ-BE-S3-002 (Update Instruction):** `OrchestratorAgent` instruction updated to reflect actual Obsidian tools and their usage.

**Stage 4: Full End-to-End V1.0 System Integration & Test**

*   **Goal:** Ensure all V1.0 components work together seamlessly.
*   **3.6. System Integration Testing:**
    *   **REQ-SYS-S4-001:** Start ADK Agent Backend (which starts Intelligent Obsidian MCP Server). Load Obsidian Plugin.
    *   **REQ-SYS-S4-002 (Scenarios):**
        *   User successfully asks for content of an existing note.
        *   User successfully asks to create a new note; note appears in vault.
        *   User successfully asks to search notes with a keyword; relevant note titles/paths are returned.
        *   User has a general conversation; agent responds via LLM.
        *   Conversation context is maintained within the side panel session.
    *   **REQ-SYS-S4-003 (Error Handling):** Test "note not found" and ensure a user-friendly error is propagated to the UI.

**4. Non-Functional Requirements (NFRs)**

*   **NFR-001 (Performance):** Local performance for V1 chat interactions should be responsive, without excessive delays for simple operations.
*   **NFR-002 (Usability - Developer):** Setup for local development (starting backend, configuring vault path) shall be clearly documented for the primary developer.
*   **NFR-003 (Reliability):** The system shall gracefully handle and display basic errors (e.g., note not found, backend service not running) in the plugin UI.
*   **NFR-004 (Modularity):** Obsidian Plugin, ADK Backend, and Obsidian MCP Server shall be testable independently to a practical extent for V1.

**5. Acceptance Criteria for Overall Project V1.0**

*   **AC-V1-01:** All components (Obsidian Plugin, ADK Backend, Intelligent Obsidian MCP Server) start and connect successfully as per the architecture.
*   **AC-V1-02:** User can send a message via the Obsidian Plugin UI and receive a basic conversational response from the LLM via the ADK Backend.
*   **AC-V1-03:** User can request the content of an existing Obsidian note via the plugin; the ADK agent uses the Obsidian MCP Server's `get_obsidian_note_content` tool, and the content is displayed in the chat.
*   **AC-V1-04:** User can request the creation of a new Obsidian note (title and content) via the plugin; the ADK agent uses the Obsidian MCP Server's `create_obsidian_note` tool, and the note is created in the vault.
*   **AC-V1-05:** User can perform a keyword search for Obsidian notes via the plugin; the ADK agent uses the Obsidian MCP Server's `keyword_search_notes` tool, and a list of matching note titles/paths is displayed.
*   **AC-V1-06:** Conversation history is maintained within a single chat session in the Obsidian plugin UI (verified by contextual LLM responses).
*   **AC-V1-07:** Basic errors (e.g., "note not found" from MCP server) are relayed and displayed in the Obsidian plugin UI.
*   **AC-V1-08:** LLM API key for the ADK Backend and vault path for the Obsidian MCP Server are configurable (via `.env` / env var or dev-time constant).

**6. Future Considerations (Post V1.0)**

*   Integrate Nomic embeddings and vector search into Obsidian MCP Server.
*   Integrate Gmail & Calendar MCP Servers & tools (requiring OAuth 2.0).
*   Implement SSE for streaming responses in the UI.
*   Persistent session storage for ADK Backend.
*   Advanced error handling and UI/UX polish.
*   User-configurable settings in the Obsidian Plugin (vault path, backend URL).
*   Investigate robust methods for managing backend processes for end-users.
*   Expand to a multi-agent architecture within the ADK backend for better task delegation.

---