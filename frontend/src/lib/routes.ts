export const routes = {
  home: "/",
  login: "/auth/login",
  signup: "/auth/signup",
  workspace: "/workspace",
  upload: "/upload",
  profile: "/profile",
} as const;

export type RouteKey = keyof typeof routes;
