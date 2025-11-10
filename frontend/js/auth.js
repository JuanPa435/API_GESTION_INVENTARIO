// Toggle de visibilidad de contraseña y validación simple

function initPasswordToggles() {
  document.querySelectorAll('[data-toggle="password"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const inputId = btn.getAttribute('data-target');
      const input = document.getElementById(inputId);
      if (!input) return;
      const isPwd = input.type === 'password';
      input.type = isPwd ? 'text' : 'password';
      const icon = btn.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
      }
    });
  });
}

function initRegisterValidation() {
  const pwd = document.getElementById('password');
  const confirm = document.getElementById('confirm_password');
  const error = document.getElementById('confirm_error');
  if (!pwd || !confirm) return;

  const check = () => {
    if (confirm.value && pwd.value !== confirm.value) {
      if (error) error.classList.add('show');
    } else {
      if (error) error.classList.remove('show');
    }
  };
  pwd.addEventListener('input', check);
  confirm.addEventListener('input', check);
}

function ensureToastContainer() {
    let c = document.querySelector('.toast-container');
    if (!c) {
        c = document.createElement('div');
        c.className = 'toast-container';
        document.body.appendChild(c);
    }
    return c;
}

function showToast(message, type = 'success') {
    const container = ensureToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i><div class="toast-message">${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-6px)';
        setTimeout(() => toast.remove(), 200);
    }, 2200);
}

document.addEventListener('DOMContentLoaded', () => {
    // Si ya hay token y estamos en login o registro, redirigir al menú y reemplazar historial
    const path = location.pathname;
    const hasToken = !!localStorage.getItem('token');
    if (hasToken && (path.endsWith('/login.html') || path.endsWith('/register.html'))) {
        return window.location.replace('/pages/menu.html');
    }

  initPasswordToggles();
  initRegisterValidation();
});
// Funciones de autenticación
class Auth {
    static async login(username, password) {
        try {
            const data = await API.login(username, password);
            localStorage.setItem('token', data.access_token);
            return true;
        } catch (error) {
            console.error('Error en login:', error);
            throw error;
        }
    }

    static async register(email, username, password) {
        try {
            await API.register({
                email,
                username,
                password,
                role: 'employee' // Por defecto, los usuarios se registran como empleados
            });
            return true;
        } catch (error) {
            console.error('Error en registro:', error);
            throw error;
        }
    }

    static logout() {
        localStorage.removeItem('token');
        window.location.reload();
    }

    static isAuthenticated() {
        return localStorage.getItem('token') !== null;
    }
}

// Event Listeners para formularios de autenticación
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const showRegisterLink = document.getElementById('showRegister');
    const showLoginLink = document.getElementById('showLogin');
    const logoutButton = document.getElementById('logout');
    // Manejar el botón específico de "Volver al inicio" en el formulario de login
    const loginBackToLanding = document.getElementById('loginBackToLanding');
    if (loginBackToLanding) {
        loginBackToLanding.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Obtener las referencias a los elementos necesarios
            const landingPage = document.getElementById('landingPage');
            const authContainer = document.getElementById('authContainer');

            // Cambiar el display a flex antes de la animación
            landingPage.style.display = 'flex';
            landingPage.style.opacity = '0';
            
            // Ocultar el contenedor de autenticación
            authContainer.style.opacity = '0';
            
            // Esperar a que termine la animación de fade out
            setTimeout(() => {
                // Ocultar completamente el contenedor de autenticación
                authContainer.classList.add('hidden');
                
                // Mostrar la página de inicio con animación
                landingPage.classList.remove('hidden');
                landingPage.style.opacity = '1';
            }, 300);
        });
    }

    // Manejar el botón de "Volver al inicio" en el formulario de registro
    const registerBackToLanding = document.getElementById('registerBackToLanding');
    if (registerBackToLanding) {
        registerBackToLanding.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const landingPage = document.getElementById('landingPage');
            const authContainer = document.getElementById('authContainer');

            landingPage.style.display = 'flex';
            landingPage.style.opacity = '0';
            
            authContainer.style.opacity = '0';
            
            setTimeout(() => {
                authContainer.classList.add('hidden');
                landingPage.classList.remove('hidden');
                landingPage.style.opacity = '1';
            }, 300);
        });
    }
    const authContainer = document.getElementById('authContainer');
    const landingPage = document.getElementById('landingPage');

    // Función para mostrar/ocultar el contenedor de autenticación
    function toggleAuthContainer(show) {
        if (show) {
            landingPage.style.display = 'none';
            authContainer.style.display = 'flex';
            authContainer.style.opacity = '0';
            setTimeout(() => {
                authContainer.style.opacity = '1';
            }, 10);
        } else {
            authContainer.style.opacity = '0';
            setTimeout(() => {
                authContainer.style.display = 'none';
                landingPage.style.display = 'block';
                setTimeout(() => {
                    landingPage.style.opacity = '1';
                }, 10);
            }, 300);
        }
    }

    // Alternar entre formularios
    showRegisterLink?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.remove('hidden');
    });

    showLoginLink?.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('registerForm').classList.add('hidden');
        document.getElementById('loginForm').classList.remove('hidden');
    });

    // Botones para volver a la landing page
    const loginBackButton = document.querySelector('#loginBackToLanding');
    const registerBackButton = document.querySelector('#registerBackToLanding');

    // Manejador para el botón de volver en el formulario de login
    loginBackButton?.addEventListener('click', (e) => {
        e.preventDefault();
        toggleAuthContainer(false);
    });

    // Manejador para el botón de volver en el formulario de registro
    registerBackButton?.addEventListener('click', (e) => {
        e.preventDefault();
        toggleAuthContainer(false);
    });

    // Botones de la landing page para mostrar auth
    document.getElementById('loginButton')?.addEventListener('click', () => {
        toggleAuthContainer(true);
        document.getElementById('registerForm').classList.add('hidden');
        document.getElementById('loginForm').classList.remove('hidden');
    });

    document.getElementById('registerButton')?.addEventListener('click', () => {
        toggleAuthContainer(true);
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.remove('hidden');
    });

    // Manejar envío del formulario de login (solo si existe)
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const identityInput = document.getElementById('identity');
            const pwdInput = document.getElementById('password');
            if (!identityInput || !pwdInput) return;
            const username = identityInput.value.trim();
            const password = pwdInput.value;

            try {
                const body = new URLSearchParams();
                body.append('username', username);
                body.append('password', password);
                const res = await fetch('/token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body
                });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    throw new Error(data.detail || 'No se pudo iniciar sesión');
                }
                const data = await res.json();
                if (data && data.access_token) {
                    localStorage.setItem('token', data.access_token);
                    window.location.replace('/pages/menu.html');
                } else {
                    throw new Error('Respuesta inválida del servidor');
                }
            } catch (err) {
                showToast('Error al iniciar sesión: ' + (err?.message || err), 'error');
            }
        });
    }

    // Manejar envío del formulario de registro
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('email');
            const pwdInput = document.getElementById('password');
            const confirmInput = document.getElementById('confirm_password');
            const error = document.getElementById('confirm_error');
            if (!emailInput || !pwdInput) return;

            if (confirmInput && pwdInput.value !== confirmInput.value) {
                error?.classList.add('show');
                return;
            }

            const email = emailInput.value.trim();
            const password = pwdInput.value;
            const usernameInput = document.getElementById('username');
            const username = usernameInput ? usernameInput.value.trim() : email.split('@')[0];

            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, username })
                });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    throw new Error(data.detail || 'No se pudo registrar');
                }
                showToast('Cuenta creada con éxito. Redirigiendo al inicio de sesión…', 'success');
                setTimeout(() => { window.location.replace('/login.html'); }, 1200);
            } catch (err) {
                showToast('Error en el registro: ' + (err?.message || err), 'error');
            }
        });
    }

    // Manejar cierre de sesión
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            Auth.logout();
        });
    }

    // Verificar autenticación al cargar
    // Evitar errores si no hay dashboard ni formularios
});