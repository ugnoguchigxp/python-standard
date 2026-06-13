import type { QueryClient } from "@tanstack/react-query";
import { createRootRouteWithContext, Link, Outlet } from "@tanstack/react-router";
import { Database, Home, LayoutGrid, LogOut, Shield } from "lucide-react";
import { useAuth } from "../lib/auth";
import { defaultShowcaseTableSearch } from "../showcase-table-search";

interface RouterContext {
  queryClient: QueryClient;
  auth: ReturnType<typeof useAuth>;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const { auth } = Route.useRouteContext();

  return (
    <div className="app-root min-h-screen">
      <header className="topbar">
        <Link to="/" className="brand">
          <Database className="icon" />
          <span>fastapi-standard</span>
        </Link>
        <div className="topbar-actions">
          <nav className="menu-nav" aria-label="Primary">
            <Link
              to="/"
              className="menu-link"
              activeProps={{ className: "menu-link active" }}
            >
              <Home className="icon" />
              Home
            </Link>
            <Link
              to="/showcase"
              search={defaultShowcaseTableSearch}
              className="menu-link"
              activeProps={{ className: "menu-link active" }}
            >
              <LayoutGrid className="icon" />
              Showcase
            </Link>
            <Link
              to="/login"
              className="menu-link"
              activeProps={{ className: "menu-link active" }}
            >
              Login
            </Link>
          </nav>
          {auth.user ? (
            <>
              <div className="auth-chip">
                <Shield className="icon" />
                <span>
                  {auth.user.email} ({auth.user.is_superuser ? "superuser" : "user"})
                </span>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={() => void auth.logout()}
                disabled={auth.isLoading}
                aria-label="Logout"
                title="Logout"
              >
                <LogOut className="icon" />
              </button>
            </>
          ) : null}
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
