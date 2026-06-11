import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../lib/auth";
import { Loader2 } from "lucide-react";

export const Route = createFileRoute("/oauth/callback")({
  component: OAuthCallbackPage,
});

function OAuthCallbackPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const code = searchParams.get("code");

    if (!code) {
      setError("No authorization code provided.");
      return;
    }

    const exchangeCode = async () => {
      try {
        const res = await fetch(`/api/auth/oauth/callback?code=${code}`);
        if (!res.ok) {
          throw new Error("Failed to exchange authorization code");
        }

        const data = await res.json();
        
        // Fetch user profile info using the new token
        const meRes = await fetch("/api/auth/me", {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        });

        if (!meRes.ok) {
          throw new Error("Failed to fetch user profile details");
        }

        const userData = await meRes.ok ? await meRes.json() : { id: 999, email: data.email, is_superuser: false };
        auth.login(userData, data.access_token);
        navigate({ to: "/" });
      } catch (err: any) {
        setError(err.message || "OAuth authentication failed");
      }
    };

    exchangeCode();
  }, []);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-65px)] gap-2">
        <h1 className="text-xl font-bold text-destructive">OAuth Callback Failure</h1>
        <p className="text-muted-foreground">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-65px)] gap-4">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="text-muted-foreground text-sm">Exchanging credentials...</p>
    </div>
  );
}
