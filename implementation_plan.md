# Binary Matrix 8x8 HDMI Switcher - Home Assistant Integration Plan

## Overview
This document outlines the implementation plan for integrating a Binary Matrix 8x8 HDMI switcher with Home Assistant via telnet connection.

## Technical Specifications

### Connection Details
- IP Address: 192.168.4.200
- Port: 23
- Username: admin
- Password: 123

### Command Structure
- Output to Input mapping: `XXYY` (XX=output number 01-08, YY=input number 01-08)
- Status Command: `STMAP` 
- Example command: `0102` (connects output 01 to input 02)

### Expected Responses
```
# Login Sequence
Telnet Server
(for this demo, type 'admin' for the login and '123' for the password.)
Login: admin
Password: 123

Logged in successfully

Press 'q' to quit
>

# Status Map Response
>STMAP
STMAP
o01i02
o02i05
o03i01
o04i02
o05i01
o06i05
o07i07
o08i03
>
```

## Component Architecture

```mermaid
graph TD
    A[Home Assistant Core] --> B[Binary Matrix Integration]
    B --> C[Configuration]
    B --> D[Matrix Controller]
    D --> E[Telnet Client]
    E --> F[Matrix Switch Device]
    B --> G[UI Panel]
    
    subgraph Configuration
        C --> C1[IP: 192.168.4.200]
        C --> C2[Username/Password]
        C --> C3[Port: 23]
    end
    
    subgraph Controller Logic
        D --> D1[State Management]
        D --> D2[Command Parser]
        D --> D3[Status Monitor]
    end
    
    subgraph UI Components
        G --> G1[8x8 Matrix Grid]
        G --> G2[Current Mapping Display]
        G --> G3[Quick Actions]
    end
```

## Implementation Components

### 1. Directory Structure
```
custom_components/
└── binary_matrix/
    ├── __init__.py
    ├── manifest.json
    ├── config_flow.py
    ├── const.py
    ├── matrix_controller.py
    ├── strings.json
    └── translations/
```

### 2. Core Components

#### Telnet Client
- Handle connection establishment
- Authentication sequence
- Command sending/receiving
- Auto-reconnect on failure
- Response parsing

#### Matrix Controller
- State management for 8x8 matrix
- Command queuing and execution
- Regular status polling (STMAP)
- State change notifications

#### Home Assistant Integration
- Config flow for setup
- Service registration
- State updates
- Event handling

### 3. UI Implementation

```mermaid
graph LR
    A[Matrix Panel] --> B[8x8 Grid]
    B --> C[Interactive Buttons]
    C --> D[Current Mapping]
    C --> E[Connection Status]
    C --> F[Quick Presets]
```

## Communication Flow

```mermaid
sequenceDiagram
    participant HA as Home Assistant
    participant IC as Integration Component
    participant TC as Telnet Client
    participant MS as Matrix Switch

    HA->>IC: Initialize Integration
    IC->>TC: Open Connection
    TC->>MS: Connect
    MS-->>TC: Login Prompt
    TC->>MS: Send Username
    MS-->>TC: Password Prompt
    TC->>MS: Send Password
    MS-->>TC: Login Success
    TC-->>IC: Ready State
    
    loop State Monitoring
        IC->>TC: Send STMAP
        TC->>MS: STMAP Command
        MS-->>TC: Matrix Status
        TC-->>IC: Parse Status
        IC-->>HA: Update State
    end

    Note over HA,MS: User Input Handling
    HA->>IC: Switch Request
    IC->>TC: Format Command (e.g., "0102")
    TC->>MS: Send Command
    MS-->>TC: Command Echo
    TC->>MS: STMAP
    MS-->>TC: New Status
    TC-->>IC: Update State
    IC-->>HA: Refresh UI
```

## Configuration Example

```yaml
binary_matrix:
  host: 192.168.4.200
  port: 23
  username: "admin"
  password: "123"
  scan_interval: 30  # Status check interval in seconds
```

## Error Handling

1. Connection Issues
   - Automatic reconnection attempts
   - Exponential backoff
   - Status reporting to HA

2. Command Failures
   - Retry logic
   - State verification
   - Error reporting

3. State Synchronization
   - Regular status polling
   - State verification after commands
   - Conflict resolution

## Implementation Steps

1. **Phase 1: Core Implementation**
   - Basic telnet client
   - Authentication handling
   - Command/response parsing
   - State management

2. **Phase 2: HA Integration**
   - Config flow setup
   - Service registration
   - State management
   - Basic UI

3. **Phase 3: UI Enhancement**
   - Matrix grid implementation
   - Status visualization
   - Quick actions
   - Presets

4. **Phase 4: Testing & Refinement**
   - Connection stability
   - Error handling
   - Performance optimization
   - Documentation