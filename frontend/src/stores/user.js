import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/api";

export const useUserStore = defineStore("user", () => {
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));
  const token = ref(localStorage.getItem("token") || "");

  function setAuth(newToken, newUser) {
    token.value = newToken;
    user.value = newUser;
    localStorage.setItem("token", newToken);
    localStorage.setItem("user", JSON.stringify(newUser));
  }

  function logout() {
    token.value = "";
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }

  async function login(username, password) {
    const res = await api.post("/auth/login", { username, password });
    setAuth(res.token, res.user);
    return res;
  }

  async function register(username, email, password) {
    const res = await api.post("/auth/register", { username, email, password });
    setAuth(res.token, res.user);
    return res;
  }

  async function fetchUser() {
    const res = await api.get("/auth/me");
    user.value = res.user;
    localStorage.setItem("user", JSON.stringify(res.user));
  }

  return { user, token, login, register, logout, fetchUser, setAuth };
});
