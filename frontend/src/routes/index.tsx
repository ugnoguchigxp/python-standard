import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Code, Database, Sparkles, ShieldCheck, Cpu } from "lucide-react";
import { Button } from "@/components/ui";

export const Route = createFileRoute("/")({
  component: LandingPage,
});

function LandingPage() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-65px)]">
      {/* Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center text-center px-4 py-16 md:py-24 bg-linear-to-b from-card/30 to-background relative overflow-hidden">
        {/* Decorative subtle background gradient */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl space-y-6 relative z-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-sm font-medium text-primary mb-2 animate-pulse">
            <Sparkles className="h-4 w-4" />
            FastAPI Standard v1.0.0
          </div>
          
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-balance">
            Enterprise-grade Python + React Starter Kit
          </h1>
          
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto text-balance">
            A production-ready monolithic template. Powered by FastAPI, SQLModel, Alembic, React, Vite, Tailwind CSS v4, and TanStack Router & Query.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Button asChild size="lg" className="shadow-lg hover:shadow-primary/10 transition-all">
              <Link to="/showcase" className="flex items-center gap-2">
                Explore Showcase
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <a href="/api/docs" target="_blank" rel="noopener noreferrer">
                Open OpenAPI Docs
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="border-t border-border bg-card/10 py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-center mb-12">Architecture Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="space-y-3 p-5 rounded-xl border border-border bg-card/50 hover:bg-card hover:shadow-md transition-all">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg">FastAPI Backend</h3>
              <p className="text-sm text-muted-foreground">
                High-performance API layer with dependency injection, async request handling, security middlewares, and slowapi rate-limiting.
              </p>
            </div>

            <div className="space-y-3 p-5 rounded-xl border border-border bg-card/50 hover:bg-card hover:shadow-md transition-all">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Database className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg">SQLModel & Alembic</h3>
              <p className="text-sm text-muted-foreground">
                Unified Pydantic + SQLAlchemy model declarations. Database migrations are handled programmatically with Alembic.
              </p>
            </div>

            <div className="space-y-3 p-5 rounded-xl border border-border bg-card/50 hover:bg-card hover:shadow-md transition-all">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Code className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg">React & Vite</h3>
              <p className="text-sm text-muted-foreground">
                Modern frontend with Tailwind CSS v4, shadcn/ui components, and automatic file-based routing with TanStack Router.
              </p>
            </div>

            <div className="space-y-3 p-5 rounded-xl border border-border bg-card/50 hover:bg-card hover:shadow-md transition-all">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg">Security & Quality</h3>
              <p className="text-sm text-muted-foreground">
                CORS controls, secure HTTP headers, silent token refresh, ruff linting/formatting, and pytest test suite.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 text-center text-sm text-muted-foreground bg-background">
        <p>© {new Date().getFullYear()} FastAPI Standard. All rights reserved.</p>
      </footer>
    </div>
  );
}
