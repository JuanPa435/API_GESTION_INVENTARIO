// Variables globales
let currentCompanyId = null;
let currentEditingProductId = null;
let productsData = [];
const API_BASE = "http://localhost:8000";

// Inicialización
document.addEventListener("DOMContentLoaded", async () => {
  initializePage();
});

// Inicializar la página
async function initializePage() {
  // Obtener empresa actual de localStorage
  let userData = JSON.parse(localStorage.getItem("user_data"));
  
  // Si no está en user_data, intentar obtener del token
  if (!userData || !userData.company_id) {
    // Intentar obtener company_id de la URL
    const params = new URLSearchParams(window.location.search);
    const urlCompanyId = params.get("company_id");
    
    if (urlCompanyId) {
      currentCompanyId = parseInt(urlCompanyId);
      localStorage.setItem("user_data", JSON.stringify({ company_id: currentCompanyId }));
    } else {
      // Intentar obtener la primera compañía del usuario desde la API
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          showToast("No hay sesión activa", "error");
          setTimeout(() => {
            window.location.href = "/login.html";
          }, 2000);
          return;
        }
        
        const response = await fetch(`${API_BASE}/api/companies/my`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          const companies = await response.json();
          if (companies.length > 0) {
            currentCompanyId = companies[0].id;
            localStorage.setItem("user_data", JSON.stringify({ company_id: currentCompanyId }));
          } else {
            showToast("No perteneces a ninguna compañía", "error");
            setTimeout(() => {
              window.location.href = "/pages/menu.html";
            }, 2000);
            return;
          }
        } else {
          showToast("Error al obtener la empresa", "error");
          setTimeout(() => {
            window.location.href = "/pages/menu.html";
          }, 2000);
          return;
        }
      } catch (error) {
        console.error("Error al obtener empresa:", error);
        showToast("Error al obtener la empresa", "error");
        setTimeout(() => {
          window.location.href = "/pages/menu.html";
        }, 2000);
        return;
      }
    }
  } else {
    currentCompanyId = userData.company_id;
  }

  console.log("Empresa ID:", currentCompanyId);

  // Configurar event listeners
  setupEventListeners();

  // Cargar productos
  await loadProducts();

  // Inicializar menú móvil
  initMobileMenu();
}

// Configurar event listeners
function setupEventListeners() {
  // Botones para agregar producto
  document.getElementById("btn-add-product")?.addEventListener("click", openAddModal);
  document.getElementById("btn-add-first")?.addEventListener("click", openAddModal);

  // Modal
  document.getElementById("btn-close-modal")?.addEventListener("click", closeModal);
  document.getElementById("btn-cancel")?.addEventListener("click", closeModal);
  document.getElementById("product-form")?.addEventListener("submit", handleSaveProduct);

  // Búsqueda y filtros
  document.getElementById("search-products")?.addEventListener("input", handleSearch);
  document.getElementById("filter-stock")?.addEventListener("change", handleFilter);

  // Modal de eliminación
  document.getElementById("btn-cancel-delete")?.addEventListener("click", closeDeleteModal);
  document.getElementById("btn-confirm-delete")?.addEventListener("click", handleConfirmDelete);
}

// Cargar productos
async function loadProducts() {
  const loadingEl = document.getElementById("loading");
  const tableEl = document.getElementById("products-table");
  const noProductsEl = document.getElementById("no-products");
  const tbodyEl = document.getElementById("products-tbody");

  try {
    loadingEl?.classList.remove("hidden");
    tableEl?.classList.add("hidden");
    noProductsEl?.classList.add("hidden");

    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}/api/company/${currentCompanyId}/items/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Error al cargar productos");
    }

    productsData = await response.json();

    if (productsData.length === 0) {
      loadingEl?.classList.add("hidden");
      noProductsEl?.classList.remove("hidden");
      return;
    }

    renderProducts(productsData);
    loadingEl?.classList.add("hidden");
    tableEl?.classList.remove("hidden");
  } catch (error) {
    console.error("Error loading products:", error);
    showToast("Error al cargar productos", "error");
    loadingEl?.classList.add("hidden");
  }
}

// Renderizar productos en la tabla
function renderProducts(products) {
  const tbodyEl = document.getElementById("products-tbody");
  if (!tbodyEl) return;

  tbodyEl.innerHTML = products
    .map(
      (product) => `
    <tr>
      <td class="product-name">${escapeHtml(product.name)}</td>
      <td>${escapeHtml(product.description || "-")}</td>
      <td>
        <strong>${product.quantity}</strong>
      </td>
      <td>${product.min_quantity}</td>
      <td>
        ${getStatusBadge(product.quantity, product.min_quantity)}
      </td>
      <td>
        <div class="product-actions">
          <button class="btn-action" title="Editar" onclick="openEditModal(${product.id})">
            <i class="fas fa-edit"></i>
          </button>
          <button class="btn-action btn-delete" title="Eliminar" onclick="openDeleteModal(${product.id})">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </td>
    </tr>
  `
    )
    .join("");
}

// Obtener badge de estado
function getStatusBadge(quantity, minQuantity) {
  if (quantity === 0) {
    return '<span class="product-status status-critical"><i class="fas fa-circle"></i> Sin Stock</span>';
  } else if (quantity <= minQuantity) {
    return '<span class="product-status status-low"><i class="fas fa-circle"></i> Stock Bajo</span>';
  } else {
    return '<span class="product-status status-normal"><i class="fas fa-circle"></i> Normal</span>';
  }
}

// Abrir modal para agregar producto
function openAddModal() {
  currentEditingProductId = null;
  document.getElementById("modal-title").textContent = "Agregar Producto";
  document.getElementById("btn-submit").textContent = "Guardar Producto";
  document.getElementById("product-form").reset();
  document.getElementById("product-modal").classList.remove("hidden");
}

// Abrir modal para editar producto
async function openEditModal(productId) {
  currentEditingProductId = productId;
  const product = productsData.find((p) => p.id === productId);

  if (!product) {
    showToast("Producto no encontrado", "error");
    return;
  }

  document.getElementById("modal-title").textContent = "Editar Producto";
  document.getElementById("btn-submit").textContent = "Actualizar Producto";
  document.getElementById("product-name").value = product.name;
  document.getElementById("product-description").value = product.description || "";
  document.getElementById("product-quantity").value = product.quantity;
  document.getElementById("product-min-quantity").value = product.min_quantity;

  document.getElementById("product-modal").classList.remove("hidden");
}

// Cerrar modal
function closeModal() {
  document.getElementById("product-modal").classList.add("hidden");
  currentEditingProductId = null;
}

// Guardar producto
async function handleSaveProduct(e) {
  e.preventDefault();

  const name = document.getElementById("product-name").value.trim();
  const description = document.getElementById("product-description").value.trim();
  const quantity = parseInt(document.getElementById("product-quantity").value);
  const minQuantity = parseInt(document.getElementById("product-min-quantity").value);

  if (!name) {
    showToast("El nombre del producto es obligatorio", "warning");
    return;
  }

  if (isNaN(quantity) || quantity < 0) {
    showToast("La cantidad debe ser un número válido", "warning");
    return;
  }

  if (isNaN(minQuantity) || minQuantity < 0) {
    showToast("El stock mínimo debe ser un número válido", "warning");
    return;
  }

  const productData = {
    name,
    description: description || null,
    quantity,
    min_quantity: minQuantity,
    company_id: currentCompanyId,
  };

  try {
    const token = localStorage.getItem("token");
    
    if (!token) {
      showToast("No hay sesión activa. Por favor recarga la página.", "error");
      return;
    }

    if (!currentCompanyId) {
      showToast("No se pudo identificar la empresa. Por favor recarga la página.", "error");
      return;
    }

    console.log("Guardando producto:", productData);
    console.log("Token:", token.substring(0, 20) + "...");
    
    let response;

    if (currentEditingProductId) {
      // Editar
      response = await fetch(`${API_BASE}/api/items/${currentEditingProductId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(productData),
      });
    } else {
      // Crear
      response = await fetch(`${API_BASE}/api/items/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(productData),
      });
    }

    console.log("Respuesta del servidor:", response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error del servidor:", errorData);
      throw new Error(errorData.detail || "Error al guardar producto");
    }

    const savedProduct = await response.json();
    console.log("Producto guardado:", savedProduct);

    closeModal();
    await loadProducts();
    showToast(
      currentEditingProductId ? "Producto actualizado" : "Producto creado",
      "success"
    );
  } catch (error) {
    console.error("Error saving product:", error);
    showToast("Error al guardar producto: " + error.message, "error");
  }
}

// Abrir modal de eliminación
function openDeleteModal(productId) {
  currentEditingProductId = productId;
  document.getElementById("delete-modal").classList.remove("hidden");
}

// Cerrar modal de eliminación
function closeDeleteModal() {
  document.getElementById("delete-modal").classList.add("hidden");
  currentEditingProductId = null;
}

// Confirmar eliminación
async function handleConfirmDelete() {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}/api/items/${currentEditingProductId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Error al eliminar producto");
    }

    closeDeleteModal();
    await loadProducts();
    showToast("Producto eliminado", "success");
  } catch (error) {
    console.error("Error deleting product:", error);
    showToast("Error al eliminar producto", "error");
  }
}

// Búsqueda
function handleSearch(e) {
  const searchTerm = e.target.value.toLowerCase();
  const filtered = productsData.filter(
    (product) =>
      product.name.toLowerCase().includes(searchTerm) ||
      (product.description && product.description.toLowerCase().includes(searchTerm))
  );
  renderProducts(filtered);
}

// Filtros
function handleFilter(e) {
  const filterValue = e.target.value;
  let filtered = productsData;

  if (filterValue === "low") {
    filtered = productsData.filter((p) => p.quantity <= p.min_quantity && p.quantity > 0);
  } else if (filterValue === "out") {
    filtered = productsData.filter((p) => p.quantity === 0);
  }

  renderProducts(filtered);
}

// Mostrar toast
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  if (!toast) return;

  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}

// Escapar HTML
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Menú móvil
function initMobileMenu() {
  const menuToggle = document.querySelector(".menu-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      navLinks.classList.toggle("active");
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("active");
      });
    });
  }
}
