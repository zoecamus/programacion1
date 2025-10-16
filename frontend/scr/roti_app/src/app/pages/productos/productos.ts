import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService, UserRole } from '../../services/auth.services';
import { ProductosService, Producto, Categoria } from '../../services/productos.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './productos.html',
  styleUrl: './productos.css'
})
export class ProductosComponent implements OnInit {
  currentUserRole: UserRole | null = null;
  
  // Carrito
  carrito: { producto: Producto, cantidad: number }[] = [];
  mostrarCarrito: boolean = false;
  
  // Modal editar producto
  mostrarModalEditar: boolean = false;
  productoEditando: Producto | null = null;
  
  // Filtros
  busqueda: string = '';
  categoriaSeleccionada: string = 'todas';
  
  categorias: Categoria[] = [];
  productos: Producto[] = [];
  loading: boolean = true;
  error: string = '';

  constructor(
    public authService: AuthService,
    private productosService: ProductosService,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarCategorias();
    this.cargarProductos();
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // ✅ FUNCIÓN CERRAR SESIÓN
  cerrarSesion() {
    if (confirm('¿Estás seguro de cerrar sesión?')) {
      this.authService.logout();
      this.carrito = [];
      this.router.navigate(['/login']);
    }
  }

  cargarCategorias() {
    this.productosService.getCategorias().subscribe({
      next: (data) => {
        console.log('Categorías cargadas:', data);
        this.categorias = data;
      },
      error: (error) => {
        console.error('Error al cargar categorías:', error);
      }
    });
  }

  cargarProductos() {
    this.loading = true;
    this.productosService.getProductos({ per_page: 100 }).subscribe({
      next: (data) => {
        console.log('Productos cargados:', data);
        this.productos = data.productos || data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar productos:', error);
        this.error = 'Error al cargar los productos';
        this.loading = false;
      }
    });
  }

  get productosFiltrados(): Producto[] {
    let filtrados = this.productos;
    
    // Si no es admin, solo mostrar productos con stock
    if (this.currentUserRole !== 'Administrador') {
      filtrados = filtrados.filter(p => p.stock > 0);
    }
    
    // Filtrar por categoría
    if (this.categoriaSeleccionada !== 'todas') {
      const categoriaId = parseInt(this.categoriaSeleccionada);
      filtrados = filtrados.filter(p => p.id_categoria === categoriaId);
    }
    
    // Filtrar por búsqueda
    if (this.busqueda) {
      const termino = this.busqueda.toLowerCase();
      filtrados = filtrados.filter(p => 
        p.nombre.toLowerCase().includes(termino) || 
        p.descripcion.toLowerCase().includes(termino)
      );
    }
    
    return filtrados;
  }

  // Verificar si es admin
  isAdmin(): boolean {
    return this.currentUserRole === 'Administrador';
  }

  // Editar producto (solo admin)
  editarProducto(producto: Producto, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    
    if (!this.isAdmin()) {
      alert('Solo el administrador puede editar productos');
      return;
    }
    this.productoEditando = { ...producto };
    this.mostrarModalEditar = true;
  }

  cerrarModalEditar() {
    this.mostrarModalEditar = false;
    this.productoEditando = null;
  }

  guardarProducto() {
    if (!this.productoEditando) return;
    this.http.put<Producto>(
      `http://localhost:7000/product/${this.productoEditando.id_producto}`,
      this.productoEditando,
      { headers: this.getHeaders() }
    ).subscribe({
      next: (productoActualizado: Producto) => {
        this.productos = this.productos.map(p =>
          p.id_producto === productoActualizado.id_producto ? productoActualizado : p
        );
        alert('Producto actualizado correctamente');
        this.cerrarModalEditar();
      },
      error: (error) => {
        console.error('Error al actualizar producto:', error);
        alert('Error al actualizar el producto');
      }
    });
  }

  // Carrito
  agregarAlCarrito(producto: Producto) {
    if (producto.stock === 0) {
      alert('Producto sin stock');
      return;
    }

    const item = this.carrito.find(i => i.producto.id_producto === producto.id_producto);
    if (item) {
      if (item.cantidad < producto.stock) {
        item.cantidad++;
        alert(`${producto.nombre} agregado al carrito`);
      } else {
        alert(`No hay más stock disponible de ${producto.nombre}`);
      }
    } else {
      this.carrito.push({ producto, cantidad: 1 });
      alert(`${producto.nombre} agregado al carrito`);
    }
  }

  quitarDelCarrito(productoId: number) {
    this.carrito = this.carrito.filter(i => i.producto.id_producto !== productoId);
  }

  cambiarCantidad(productoId: number, cambio: number) {
    const item = this.carrito.find(i => i.producto.id_producto === productoId);
    if (item) {
      const nuevaCantidad = item.cantidad + cambio;
      
      if (nuevaCantidad <= 0) {
        this.quitarDelCarrito(productoId);
      } else if (nuevaCantidad <= item.producto.stock) {
        item.cantidad = nuevaCantidad;
      } else {
        alert(`No hay más stock disponible de ${item.producto.nombre}`);
      }
    }
  }

  get totalCarrito(): number {
    return this.carrito.reduce((total, item) => total + (item.producto.precio * item.cantidad), 0);
  }

  get cantidadItems(): number {
    return this.carrito.reduce((total, item) => total + item.cantidad, 0);
  }

  finalizarCompra() {
    if (this.carrito.length === 0) {
      alert('El carrito está vacío');
      return;
    }

    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) {
      alert('Debes iniciar sesión para realizar un pedido');
      this.router.navigate(['/login']);
      return;
    }

    // Preparar items del pedido
    const items = this.carrito.map(item => ({
      id_producto: item.producto.id_producto,
      producto: item.producto.nombre,
      cantidad: item.cantidad,
      precio_unitario: item.producto.precio,
      subtotal: item.producto.precio * item.cantidad
    }));

    // Preparar datos del pedido
    const nuevoPedido = {
      id_usuario: currentUser.id || currentUser.email,
      usuario_email: currentUser.email,
      usuario_nombre: currentUser.nombre,
      items: items,
      total: this.totalCarrito,
      estado: 'Recibido',
      metodo_pago: 'Efectivo',
      tipo_entrega: 'Retiro en local',
      fecha: new Date().toISOString()
    };

    console.log('📦 Creando pedido:', nuevoPedido);

    // Obtener token
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    this.http.post('http://localhost:7000/pedidos', nuevoPedido, { headers }).subscribe({
      next: (response) => {
        console.log('✅ Pedido creado exitosamente:', response);
        alert(`¡Pedido realizado con éxito! 🎉\n\nTotal: ${this.totalCarrito.toLocaleString('es-AR')}\n\nPuedes retirar tu pedido en el local cuando esté listo.`);
        this.carrito = [];
        this.mostrarCarrito = false;
        
        // Redirigir a Mis Pedidos
        this.router.navigate(['/mis-pedidos']);
      },
      error: (error) => {
        console.error('❌ Error completo al crear pedido:', error);
        console.error('Status:', error.status);
        console.error('Mensaje:', error.message);
        console.error('Error del servidor:', error.error);
        
        let mensajeError = 'Error al crear el pedido.';
        
        if (error.status === 401) {
          mensajeError = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
          this.router.navigate(['/login']);
        } else if (error.status === 400) {
          mensajeError = `Error en los datos: ${error.error?.message || 'Datos inválidos'}`;
        } else if (error.status === 500) {
          mensajeError = 'Error en el servidor. Por favor, intenta más tarde.';
        } else if (error.error?.message) {
          mensajeError = error.error.message;
        }
        
        alert(mensajeError + '\n\nRevisa la consola (F12) para más detalles.');
      }
    });
  }

  volverDashboard() {
    const redirectUrl = this.authService.getRedirectUrl();
    this.router.navigate([redirectUrl]);
  }

  getNombreCategoria(id_categoria: number): string {
    const categoria = this.categorias.find(c => c.id_categoria === id_categoria);
    return categoria ? categoria.nombre : 'Sin categoría';
  }
}