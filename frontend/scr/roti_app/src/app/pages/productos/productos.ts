import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, UserRole } from '../../services/auth.services';
import { ProductosService, Producto, Categoria } from '../../services/productos.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, FormsModule],
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
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarCategorias();
    this.cargarProductos();
  }

  private getHeaders(): HttpHeaders {
    const user = localStorage.getItem('currentUser');
    const token = user ? JSON.parse(user).access_token : '';
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
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
    // Prevenir que se propague el click
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

    this.http.put(
      `http://localhost:7000/product/${this.productoEditando.id_producto}`,
      this.productoEditando,
      { headers: this.getHeaders() }
    ).subscribe({
      next: (response: any) => {
        const index = this.productos.findIndex(p => p.id_producto === this.productoEditando!.id_producto);
        if (index !== -1) {
          this.productos[index] = { ...this.productoEditando! };
        }
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
      return;
    }

    const items = this.carrito.map(item => ({
      producto: item.producto.nombre,
      cantidad: item.cantidad,
      precio: item.producto.precio
    }));

    const nuevoPedido = {
      id_usuario: currentUser.email,
      items: items,
      total: this.totalCarrito,
      estado: 'Pendiente',
      metodo_pago: 'Efectivo'
    };

    console.log('Creando pedido:', nuevoPedido);

    this.http.post('http://localhost:7000/pedidos', nuevoPedido, { headers: this.getHeaders() }).subscribe({
      next: (response) => {
        alert(`¡Pedido realizado con éxito!\n\nTotal: $${this.totalCarrito.toLocaleString('es-AR')}\n\nPuedes retirar tu pedido cuando esté listo.`);
        this.carrito = [];
        this.mostrarCarrito = false;
      },
      error: (error) => {
        console.error('Error al crear pedido:', error);
        alert('Error al crear el pedido. Intenta de nuevo.');
      }
    });
  }

  getNombreCategoria(id_categoria: number): string {
    const categoria = this.categorias.find(c => c.id_categoria === id_categoria);
    return categoria ? categoria.nombre : 'Sin categoría';
  }
}