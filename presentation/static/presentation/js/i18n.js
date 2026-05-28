/**
 * Traducciones UI del cliente — sincronizado con LANGUAGE_CODE del HTML.
 */
window.TechRentI18n = {
  es: {
    welcome: "Bienvenido a TechRent",
    subtitle: "Inicia sesión o crea tu cuenta para alquilar equipos",
    login: "Iniciar sesión",
    register: "Registrarse",
    email: "Correo electrónico",
    password: "Contraseña",
    enter: "Entrar",
    create_account: "Crear cuenta",
    full_name: "Nombre completo",
    client_panel: "Panel del cliente",
    staff_demo: "Demo staff:",
    staff_password: "clave",
  },
  en: {
    welcome: "Welcome to TechRent",
    subtitle: "Sign in or create an account to rent equipment",
    login: "Sign in",
    register: "Sign up",
    email: "Email address",
    password: "Password",
    enter: "Sign in",
    create_account: "Create account",
    full_name: "Full name",
    client_panel: "Client dashboard",
    staff_demo: "Demo staff:",
    staff_password: "password",
  },
  apply(lang) {
    const code = (lang || "es").slice(0, 2);
    const t = this[code] || this.es;
    document.documentElement.lang = code;
    const map = {
      "auth-welcome": t.welcome,
      "auth-subtitle": t.subtitle,
      "auth-tab-login-label": t.login,
      "auth-tab-register-label": t.register,
      "label-login-email": t.email,
      "label-login-password": t.password,
      "label-register-nombre": t.full_name,
      "label-register-email": t.email,
      "label-register-password": t.password,
      "btn-login-label": t.enter,
      "btn-register-label": t.create_account,
      "header-subtitle": t.client_panel,
    };
    Object.entries(map).forEach(([id, text]) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    });
  },
};
