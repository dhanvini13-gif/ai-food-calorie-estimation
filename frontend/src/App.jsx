import { useEffect, useState } from "react";
import "./App.css";
import Dashboard from "./Dashboard";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [accountId, setAccountId] = useState(null);

  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!username.trim() || !password) {
      setError("Please enter username and password.");
      return;
    }

    if (isRegister && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const endpoint = isRegister ? "/signup" : "/login";

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      if (isRegister) {
        alert("Account created successfully!");
        setIsRegister(false);
        setUsername("");
        setPassword("");
        setConfirmPassword("");
      } else {
        if (data.account_id == null) {
          throw new Error("The server did not return an account ID.");
        }

        setAccountId(data.account_id);
        setIsLoggedIn(true);
      }
    } catch (err) {
      setError(err.message || "Unable to connect to the server.");
    } finally {
      setLoading(false);
    }
  };


if (showSplash) {
  return (
    <div className="splash-screen">
      <div className="splash-content">
        <div className="splash-logo">
          <span className="logo-n">N</span>
          <span className="logo-lens">L</span>
        </div>

        <h1>NutriLens</h1>

        <p className="splash-subtitle">
          AI-Powered Food Calorie Estimation
        </p>

        <span className="splash-tagline">
          See your food. Know your nutrition.
        </span>
      </div>
    </div>
  );
}

  if (isLoggedIn) {
    return <Dashboard accountId={accountId} />;
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="logo">
          <span className="logo-n">N</span>
          <span className="logo-lens">L</span>
        </div>

        <h1>{isRegister ? "Create account" : "Welcome"}</h1>

        <p className="subtitle">
          {isRegister
            ? "Create your account"
            : "Login to continue to your nutrition dashboard."}
        </p>

        <form onSubmit={handleSubmit}>
          <label>Username</label>
          <input
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {isRegister && (
            <>
              <label>Confirm Password</label>
              <input
                type="password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                required
              />
            </>
          )}

          {error && <div className="error">{error}</div>}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? isRegister
                ? "Creating account..."
                : "Logging in..."
              : isRegister
                ? "Create account"
                : "Login"}
          </button>
        </form>

        <div className="switch-text">
          {isRegister
            ? "Already have an account?"
            : "Don't have an account?"}

          <button
            type="button"
            className="switch-button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
              setUsername("");
              setPassword("");
              setConfirmPassword("");
            }}
          >
            {isRegister ? "Login" : "Create account"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
