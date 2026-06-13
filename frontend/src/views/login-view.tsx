import { useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { Shield } from "lucide-react";
import { useAuth } from "../lib/auth";
import { LoginDomainSection } from "../domains/auth/login-domain";
import { defaultShowcaseTableSearch } from "../showcase-table-search";

export function LoginView() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [errorText, setErrorText] = useState("");

  const loginWithPassword = async ({ email, password }: any) => {
    setBusy(true);
    setErrorText("");

    try {
      // Form URL-encoded data for OAuth2 compliance
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Invalid email or password");
      }

      const data = await res.json();
      const token = data.access_token;

      // Fetch user profile info
      const meRes = await fetch("/api/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!meRes.ok) {
        throw new Error("Failed to fetch user profile details");
      }

      const userData = await meRes.json();
      auth.login(userData, token);
      navigate({ to: "/" });
      return true;
    } catch (err: any) {
      setErrorText(err.message || "Failed to sign in. Please try again.");
      return false;
    } finally {
      setBusy(false);
    }
  };

  if (auth.isLoading) {
    return (
      <main className="center-shell">
        <div className="muted">Loading session...</div>
      </main>
    );
  }

  if (auth.user) {
    return (
      <main className="center-shell">
        <section className="signed-in-panel">
          <Shield className="icon" />
          <h1>Signed in</h1>
          <p>
            {auth.user.email} ({auth.user.is_superuser ? "superuser" : "user"})
          </p>
          <Link
            to="/showcase"
            search={defaultShowcaseTableSearch}
            className="auth-open-button"
          >
            Showcase
          </Link>
        </section>
      </main>
    );
  }

  return (
    <>
      {errorText && <div className="status error">{errorText}</div>}
      <LoginDomainSection active busy={busy} onLogin={loginWithPassword} />
    </>
  );
}
