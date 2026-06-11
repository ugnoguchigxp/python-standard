import { useState } from "react";
import type { QueryClient } from "@tanstack/react-query";
import { createRootRouteWithContext, Link, Outlet } from "@tanstack/react-router";
import { Home, LayoutGrid, LogOut, User, Menu } from "lucide-react";
import { useAuth } from "../lib/auth";
import { Avatar, Button } from "@/components/ui";

interface RouterContext {
  queryClient: QueryClient;
  auth: ReturnType<typeof useAuth>;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const { auth } = Route.useRouteContext();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="flex items-center gap-6 border-b border-border px-6 py-3 bg-card/50 backdrop-blur-md sticky top-0 z-50">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="bg-primary p-1.5 rounded-lg">
            <Home className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="font-bold text-xl tracking-tight">FastAPI Standard</span>
        </Link>

        <div className="flex items-center gap-2">
          <Button variant="ghost" asChild size="sm">
            <Link to="/showcase" className="flex items-center gap-2">
              <LayoutGrid className="h-4 w-4" />
              Showcase
            </Link>
          </Button>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-4 relative">
          {auth.user ? (
            <div>
              <div
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="cursor-pointer"
              >
                <Avatar
                  src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${auth.user.email}`}
                  fallback={auth.user.email[0].toUpperCase()}
                  size="md"
                  className="border border-border hover:border-primary/50 transition-colors"
                />
              </div>
              {dropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setDropdownOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 rounded-md border border-border bg-card p-1 shadow-md z-50 animate-in fade-in-50 zoom-in-95 duration-100">
                    <div className="px-2 py-1.5 text-xs text-muted-foreground truncate border-b border-border mb-1">
                      {auth.user.email}
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setDropdownOpen(false);
                        alert(`User Profile:\nEmail: ${auth.user?.email}\nID: ${auth.user?.id}`);
                      }}
                      className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground text-left cursor-pointer"
                    >
                      <User className="h-4 w-4" />
                      Profile
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setDropdownOpen(false);
                        auth.logout();
                      }}
                      className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-destructive hover:text-destructive-foreground text-left text-destructive cursor-pointer"
                    >
                      <LogOut className="h-4 w-4" />
                      Logout
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <Button asChild size="sm">
              <Link to="/login">Login</Link>
            </Button>
          )}
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
