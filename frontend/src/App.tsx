import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { AuthProvider, useAuth } from "./lib/auth";
import { routeTree } from "./routeTree.gen";
import { ShowcaseSettingsProvider } from "./showcase-settings-context";

const queryClient = new QueryClient();

// Set up Router instance
const router = createRouter({
  routeTree,
  defaultPreload: "intent",
  context: {
    queryClient,
    auth: undefined as any, // Set by inner context
  },
});

// Register things for typesafety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

function InnerApp() {
  const auth = useAuth();
  return <RouterProvider router={router} context={{ auth }} />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ShowcaseSettingsProvider>
        <AuthProvider>
          <InnerApp />
        </AuthProvider>
      </ShowcaseSettingsProvider>
    </QueryClientProvider>
  );
}
