import { createFileRoute } from "@tanstack/react-router";
import { LoginView } from "../views/login-view";

export const Route = createFileRoute("/login")({
  component: LoginView,
});
