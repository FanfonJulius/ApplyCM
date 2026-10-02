import { env } from "$env/dynamic/public";

// Set PUBLIC_API_BASE_URL (e.g. http://localhost:8001) to use a local backend.
export const API_BASE_URL = (env.PUBLIC_API_BASE_URL || "https://applycm-backend.onrender.com").replace(/\/+$/, "");
