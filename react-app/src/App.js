import React, { useState, useEffect } from 'react';
import { RegisterUser, LoginUser } from '../src/services/auth';

// Mock data
const mockChatSessions = [
  {
    id: 1,
    providerName: 'Dr. Sarah Johnson',
    lastMessage: 'Your appointment is confirmed for tomorrow',
    timestamp: '2024-01-15 14:30',
    unread: 2
  },
  {
    id: 2,
    providerName: 'Dr. Mike Chen',
    lastMessage: 'Thank you for scheduling',
    timestamp: '2024-01-14 09:15',
    unread: 0
  },
  {
    id: 3,
    providerName: 'Dr. Emily Brown',
    lastMessage: 'Looking forward to our session',
    timestamp: '2024-01-13 16:45',
    unread: 1
  }
];

const mockUpcomingAppointments = [
  {
    id: 1,
    date: '2024-01-16',
    time: '10:00 AM',
    providerName: 'Dr. Sarah Johnson',
    type: 'Consultation'
  },
  {
    id: 2,
    date: '2024-01-18',
    time: '2:30 PM',
    providerName: 'Dr. Mike Chen',
    type: 'Follow-up'
  }
];

const mockPastAppointments = [
  {
    id: 3,
    date: '2024-01-10',
    time: '11:00 AM',
    providerName: 'Dr. Emily Brown',
    type: 'Initial Consultation'
  }
];

const mockMessages = [
  { id: 1, sender: 'provider', message: 'Hello! How can I help you today?', timestamp: '10:30 AM' },
  { id: 2, sender: 'seeker', message: 'Hi, I would like to schedule an appointment', timestamp: '10:32 AM' },
  { id: 3, sender: 'provider', message: 'Of course! What time works best for you?', timestamp: '10:33 AM' }
];

const SeekerApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState(mockMessages);
  const [newMessage, setNewMessage] = useState('');
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [prefilledMessage, setPrefilledMessage] = useState('');
  const [editing, setEditing] = useState(false);
  const [activeAppointmentTab, setActiveAppointmentTab] = useState('upcoming');
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState('');

  // Form states
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [profileForm, setProfileForm] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    mobile: '+1-555-0123'
  });

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    const token = sessionStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Styles
  const styles = {
    container: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    },
    loginContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    },
    loginCard: {
      width: '400px',
      padding: '32px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
    },
    header: {
      height: '64px',
      backgroundColor: 'white',
      borderBottom: '1px solid #f0f0f0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px'
    },
    nav: {
      height: '48px',
      backgroundColor: '#fafafa',
      borderBottom: '1px solid #f0f0f0',
      display: 'flex',
      alignItems: 'center',
      padding: '0 24px'
    },
    navButton: {
      padding: '8px 16px',
      marginRight: '8px',
      border: 'none',
      backgroundColor: 'transparent',
      cursor: 'pointer',
      borderRadius: '4px'
    },
    activeNavButton: {
      backgroundColor: '#e6f7ff',
      color: '#1890ff'
    },
    sidebar: {
      width: '300px',
      backgroundColor: 'white',
      borderRight: '1px solid #f0f0f0',
      height: 'calc(100vh - 112px)',
      overflow: 'auto'
    },
    chatList: {
      listStyle: 'none',
      padding: 0,
      margin: 0
    },
    chatItem: {
      padding: '12px 16px',
      borderBottom: '1px solid #f5f5f5',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center'
    },
    activeChatItem: {
      backgroundColor: '#e6f7ff'
    },
    avatar: {
      width: '40px',
      height: '40px',
      borderRadius: '50%',
      backgroundColor: '#1890ff',
      color: 'white',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginRight: '12px'
    },
    chatContent: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 112px)',
      backgroundColor: 'white'
    },
    chatHeader: {
      padding: '16px',
      borderBottom: '1px solid #f0f0f0'
    },
    messageArea: {
      flex: 1,
      padding: '16px',
      overflowY: 'auto'
    },
    message: {
      marginBottom: '12px',
      display: 'flex'
    },
    messageContent: {
      maxWidth: '70%',
      padding: '8px 12px',
      borderRadius: '12px'
    },
    seekerMessage: {
      justifyContent: 'flex-end'
    },
    seekerMessageContent: {
      backgroundColor: '#1890ff',
      color: 'white'
    },
    providerMessage: {
      justifyContent: 'flex-start'
    },
    providerMessageContent: {
      backgroundColor: '#f5f5f5',
      color: 'black'
    },
    inputArea: {
      padding: '16px',
      borderTop: '1px solid #f0f0f0',
      display: 'flex',
      gap: '8px'
    },
    messageInput: {
      flex: 1,
      padding: '8px 12px',
      border: '1px solid #d9d9d9',
      borderRadius: '6px',
      outline: 'none'
    },
    sendButton: {
      padding: '8px 16px',
      backgroundColor: '#1890ff',
      color: 'white',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer'
    },
    button: {
      padding: '8px 16px',
      border: '1px solid #d9d9d9',
      borderRadius: '6px',
      cursor: 'pointer',
      backgroundColor: 'white'
    },
    primaryButton: {
      backgroundColor: '#1890ff',
      color: 'white',
      border: '1px solid #1890ff'
    },
    dangerButton: {
      color: '#ff4d4f',
      borderColor: '#ff4d4f'
    },
    input: {
      width: '100%',
      padding: '8px 12px',
      border: '1px solid #d9d9d9',
      borderRadius: '6px',
      marginBottom: '16px',
      outline: 'none'
    },
    card: {
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      marginBottom: '16px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    appointmentItem: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '16px',
      border: '1px solid #f0f0f0',
      borderRadius: '8px',
      marginBottom: '12px'
    },
    badge: {
      backgroundColor: '#ff4d4f',
      color: 'white',
      borderRadius: '10px',
      padding: '2px 6px',
      fontSize: '12px',
      marginLeft: '8px'
    },
    modal: {
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    },
    modalContent: {
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '24px',
      maxWidth: '400px',
      width: '90%'
    },
    drawer: {
      position: 'fixed',
      top: 0,
      left: sidebarVisible ? 0 : '-300px',
      width: '300px',
      height: '100vh',
      backgroundColor: 'white',
      zIndex: 1000,
      transition: 'left 0.3s ease',
      boxShadow: '2px 0 8px rgba(0,0,0,0.1)'
    },
    overlay: {
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0,0,0,0.3)',
      zIndex: 999
    }
  };

  // Helper functions
  const showNotification = (message) => {
    //alert(message); // Simple notification
  };

  const confirmAction = (message, onConfirm) => {
    if (window.confirm(message)) {
      onConfirm();
    }
  };

  // Login Component

  // Login Component
  const LoginPage = ({ setIsAuthenticated, showNotification }) => {
    const [isRegistering, setIsRegistering] = useState(false);
    const [loginForm, setLoginForm] = useState({ email: "", password: "" });
    const [registerForm, setRegisterForm] = useState({
      name: "",
      email: "",
      phone: "",
      password: "",
      role: "seeker"
    });

    const handleLoginSubmit = async (e) => {
      e.preventDefault();
      if (loginForm.email && loginForm.password) {
        

        const formData = new FormData();
        formData.append('username', loginForm.email);
        formData.append('password', loginForm.password);
        const response = await LoginUser(formData);
        console.log("Login response:", response);
        if (!response){
          showNotification("Login failed");
          return;
        }
        sessionStorage.setItem('token', response.access_token);
        setIsAuthenticated(true);
        showNotification("Login successful!");
      } else {
        showNotification("Please fill in all fields");
      }
    };

    const handleRegisterSubmit = async (e) => {
      e.preventDefault();
      if (registerForm.name && registerForm.email && registerForm.phone && registerForm.password && registerForm.role) {
        const response = await RegisterUser(registerForm)
        if (!response){
          showNotification("Registration failed");
          return;
        }
        showNotification(`Registered successfully as ${registerForm.role}!`);
        //API call
        setIsRegistering(false); // go back to login
      } else {
        showNotification("Please fill in all fields");
      }
    };

    return (
      <div style={styles.loginContainer}>
        <div style={styles.loginCard}>
          <div style={{ textAlign: "center", marginBottom: "24px" }}>
            <h2>{isRegistering ? "Create Account" : "Welcome Back"}</h2>
            <p style={{ color: "#666" }}>
              {isRegistering ? "Register to get started" : "Sign in to your account"}
            </p>
          </div>

          {!isRegistering ? (
            // LOGIN FORM
            <form onSubmit={handleLoginSubmit}>
              <div>
                <label>Email</label>
                <input
                  type="email"
                  style={styles.input}
                  placeholder="Enter your email"
                  value={loginForm.email}
                  onChange={(e) =>
                    setLoginForm({ ...loginForm, email: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <label>Password</label>
                <input
                  type="password"
                  style={styles.input}
                  placeholder="Enter your password"
                  value={loginForm.password}
                  onChange={(e) =>
                    setLoginForm({ ...loginForm, password: e.target.value })
                  }
                  required
                />
              </div>
              <button
                type="submit"
                style={{
                  ...styles.button,
                  ...styles.primaryButton,
                  width: "100%"
                }}
              >
                Login
              </button>
              <p style={{ marginTop: "16px", textAlign: "center" }}>
                New user?{" "}
                <button
                  type="button"
                  style={{ ...styles.button, border: "none", color: "#1890ff", background: "transparent", cursor: "pointer" }}
                  onClick={() => setIsRegistering(true)}
                >
                  Register here
                </button>
              </p>
            </form>
          ) : (
            // REGISTER FORM
            <form onSubmit={handleRegisterSubmit}>
              <div>
                <label>Name</label>
                <input
                  type="text"
                  style={styles.input}
                  placeholder="Enter your name"
                  value={registerForm.name}
                  onChange={(e) =>
                    setRegisterForm({ ...registerForm, name: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <label>Email</label>
                <input
                  type="email"
                  style={styles.input}
                  placeholder="Enter your email"
                  value={registerForm.email}
                  onChange={(e) =>
                    setRegisterForm({ ...registerForm, email: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <label>Phone Number</label>
                <input
                  type="tel"
                  style={styles.input}
                  placeholder="Enter your phone number"
                  value={registerForm.phone}
                  onChange={(e) =>
                    setRegisterForm({ ...registerForm, phone: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <label>Password</label>
                <input
                  type="password"
                  style={styles.input}
                  placeholder="Enter your password"
                  value={registerForm.password}
                  onChange={(e) =>
                    setRegisterForm({ ...registerForm, password: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <label>Role</label>
                <select
                  style={styles.input}
                  value={registerForm.role}
                  onChange={(e) =>
                    setRegisterForm({ ...registerForm, role: e.target.value })
                  }
                >
                  <option value="seeker">Seeker</option>
                  <option value="provider">Provider</option>
                  <option value="orchestrator">Orchestrator</option>
                  <option value="architect">Architect</option>
                </select>
              </div>
              <button
                type="submit"
                style={{
                  ...styles.button,
                  ...styles.primaryButton,
                  width: "100%"
                }}
              >
                Register
              </button>
              <p style={{ marginTop: "16px", textAlign: "center" }}>
                Already have an account?{" "}
                <button
                  type="button"
                  style={{ ...styles.button, border: "none", color: "#1890ff", background: "transparent", cursor: "pointer" }}
                  onClick={() => setIsRegistering(false)}
                >
                  Login here
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  };


  // Chat Session List Component
  const ChatSessionList = () => (
    <div>
      <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h4 style={{ margin: 0 }}>Chat Sessions</h4>
        <button style={styles.button}>+</button>
      </div>
      <ul style={styles.chatList}>
        {mockChatSessions.map((item) => (
          <li
            key={item.id}
            style={{
              ...styles.chatItem,
              ...(selectedChat?.id === item.id ? styles.activeChatItem : {})
            }}
            onClick={() => {
              setSelectedChat(item);
              if (isMobile) setSidebarVisible(false);
            }}
          >
            <div style={styles.avatar}>
              {item.providerName.charAt(0)}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                <strong>{item.providerName}</strong>
                {item.unread > 0 && (
                  <span style={styles.badge}>{item.unread}</span>
                )}
              </div>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>
                {item.lastMessage}
              </div>
              <div style={{ fontSize: '12px', color: '#999' }}>
                {item.timestamp}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );

  // Chat Window Component
  const ChatWindow = () => {
  const [newMessage, setNewMessage] = useState("");
  const [prefilledMessage, setPrefilledMessage] = useState("");

  const sendMessage = () => {
    const messageToSend = newMessage.trim();
    if (messageToSend) {
      const message = {
        id: messages.length + 1,
        sender: "seeker",
        message: messageToSend,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      setMessages([...messages, message]);
      setNewMessage("");
      setPrefilledMessage("");
    }
  };

  // Whenever prefilledMessage changes, load it into newMessage
  useEffect(() => {
    if (prefilledMessage) {
      setNewMessage(prefilledMessage);
      setPrefilledMessage(""); // consume it
    }
  }, [prefilledMessage]);

  return (
    <div style={styles.chatContent}>
      <div style={styles.chatHeader}>
        <h4 style={{ margin: 0 }}>
          {selectedChat ? selectedChat.providerName : "New Chat"}
        </h4>
      </div>

      <div style={styles.messageArea}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              ...styles.message,
              ...(msg.sender === "seeker"
                ? styles.seekerMessage
                : styles.providerMessage),
            }}
          >
            <div
              style={{
                ...styles.messageContent,
                ...(msg.sender === "seeker"
                  ? styles.seekerMessageContent
                  : styles.providerMessageContent),
              }}
            >
              <div>{msg.message}</div>
              <div
                style={{
                  fontSize: "10px",
                  opacity: 0.7,
                  marginTop: "4px",
                }}
              >
                {msg.timestamp}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.messageInput}
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button style={styles.sendButton} onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

  // Dashboard Component
  const Dashboard = () => (
    <div style={{ display: 'flex', height: 'calc(100vh - 112px)' }}>
      {isMobile && sidebarVisible && (
        <>
          <div style={styles.overlay} onClick={() => setSidebarVisible(false)}></div>
          <div style={styles.drawer}>
            <ChatSessionList />
          </div>
        </>
      )}
      {!isMobile && (
        <div style={styles.sidebar}>
          <ChatSessionList />
        </div>
      )}
      <div style={{ flex: 1 }}>
        <ChatWindow />
      </div>
    </div>
  );

  // Appointments Component
  const Appointments = () => {
    const handleReschedule = (appointment) => {
      setPrefilledMessage(`I want to reschedule my appointment with ${appointment.providerName} on ${appointment.date} at ${appointment.time}`);
      setCurrentPage('dashboard');
      showNotification('Opening chat to reschedule appointment');
    };

    const handleCancel = (appointmentId) => {
      confirmAction('Are you sure you want to cancel this appointment?', () => {
        showNotification('Appointment cancelled');
      });
    };

    return (
      <div style={{ padding: '24px' }}>
        <h2>My Appointments</h2>
        <div style={{ marginBottom: '24px' }}>
          <button
            style={{
              ...styles.navButton,
              ...(activeAppointmentTab === 'upcoming' ? styles.activeNavButton : {})
            }}
            onClick={() => setActiveAppointmentTab('upcoming')}
          >
            Upcoming
          </button>
          <button
            style={{
              ...styles.navButton,
              ...(activeAppointmentTab === 'past' ? styles.activeNavButton : {})
            }}
            onClick={() => setActiveAppointmentTab('past')}
          >
            Past
          </button>
        </div>

        {activeAppointmentTab === 'upcoming' && (
          <div>
            {mockUpcomingAppointments.map((item) => (
              <div key={item.id} style={styles.appointmentItem}>
                <div>
                  <div style={styles.avatar}>{item.providerName.charAt(0)}</div>
                </div>
                <div style={{ flex: 1, marginLeft: '12px' }}>
                  <h4 style={{ margin: '0 0 4px 0' }}>{item.providerName}</h4>
                  <div>{item.date} at {item.time}</div>
                  <div style={{ color: '#666', fontSize: '14px' }}>{item.type}</div>
                </div>
                <div>
                  <button
                    style={{...styles.button, marginRight: '8px'}}
                    onClick={() => handleReschedule(item)}
                  >
                    Reschedule
                  </button>
                  <button
                    style={{...styles.button, ...styles.dangerButton}}
                    onClick={() => handleCancel(item.id)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeAppointmentTab === 'past' && (
          <div>
            {mockPastAppointments.map((item) => (
              <div key={item.id} style={styles.appointmentItem}>
                <div>
                  <div style={styles.avatar}>{item.providerName.charAt(0)}</div>
                </div>
                <div style={{ flex: 1, marginLeft: '12px' }}>
                  <h4 style={{ margin: '0 0 4px 0' }}>{item.providerName}</h4>
                  <div>{item.date} at {item.time}</div>
                  <div style={{ color: '#666', fontSize: '14px' }}>{item.type}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Profile Component
  const Profile = () => {
    const handleSave = () => {
      showNotification('Profile updated successfully');
      setEditing(false);
    };

    return (
      <div style={{ padding: '24px', maxWidth: '600px' }}>
        <h2>Profile</h2>
        <div style={styles.card}>
          <div style={{ marginBottom: '16px' }}>
            <label>Name</label>
            <input
              style={styles.input}
              value={profileForm.name}
              disabled={!editing}
              onChange={(e) => setProfileForm({...profileForm, name: e.target.value})}
            />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label>Email</label>
            <input
              style={styles.input}
              value={profileForm.email}
              disabled={!editing}
              onChange={(e) => setProfileForm({...profileForm, email: e.target.value})}
            />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label>Mobile</label>
            <input
              style={styles.input}
              value={profileForm.mobile}
              disabled={!editing}
              onChange={(e) => setProfileForm({...profileForm, mobile: e.target.value})}
            />
          </div>
          <div>
            {editing ? (
              <>
                <button
                  style={{...styles.button, ...styles.primaryButton, marginRight: '8px'}}
                  onClick={handleSave}
                >
                  Save Changes
                </button>
                <button
                  style={styles.button}
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                style={{...styles.button, ...styles.primaryButton}}
                onClick={() => setEditing(true)}
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div style={styles.card}>
          <h4>Change Password</h4>
          <div style={{ marginBottom: '16px' }}>
            <label>Current Password</label>
            <input type="password" style={styles.input} />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label>New Password</label>
            <input type="password" style={styles.input} />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label>Confirm New Password</label>
            <input type="password" style={styles.input} />
          </div>
          <button style={{...styles.button, ...styles.primaryButton}}>
            Update Password
          </button>
        </div>
      </div>
    );
  };

  // Main Layout Component
  const MainLayout = () => {
    const menuItems = [
      { key: 'dashboard', label: 'Dashboard', icon: '💬' },
      { key: 'appointments', label: 'Appointments', icon: '📅' },
      { key: 'profile', label: 'Profile', icon: '👤' },
    ];

    const renderContent = () => {
      switch (currentPage) {
        case 'dashboard':
          return <Dashboard />;
        case 'appointments':
          return <Appointments />;
        case 'profile':
          return <Profile />;
        default:
          return <Dashboard />;
      }
    };

    const handleLogout = () => {
      
      sessionStorage.removeItem('token');
      setIsAuthenticated(false);
      showNotification('Logged out successfully');
      
    }

    return (
      <div style={styles.container}>
        <header style={styles.header}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {isMobile && currentPage === 'dashboard' && (
              <button
                style={{...styles.button, marginRight: '16px'}}
                onClick={() => setSidebarVisible(true)}
              >
                ☰
              </button>
            )}
            <h3 style={{ margin: 0, color: '#1890ff' }}>BookChat</h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ marginRight: '16px' }}>Welcome, John!</span>
            <button
              style={styles.button}
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </header>
        
        <nav style={styles.nav}>
          {menuItems.map((item) => (
            <button
              key={item.key}
              style={{
                ...styles.navButton,
                ...(currentPage === item.key ? styles.activeNavButton : {})
              }}
              onClick={() => setCurrentPage(item.key)}
            >
              <span style={{ marginRight: '8px' }}>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {renderContent()}
      </div>
    );
  };

  return (
    <div>
      {isAuthenticated ? <MainLayout /> : <LoginPage setIsAuthenticated={setIsAuthenticated} showNotification={showNotification} />}
    </div>
  );
};

export default SeekerApp;
