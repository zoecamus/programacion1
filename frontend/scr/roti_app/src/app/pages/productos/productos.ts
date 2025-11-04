import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, UserRole } from '../../services/auth.services';
import { ProductosService, Producto, Categoria } from '../../services/productos.service';
import { CarritoService } from '../../services/carrito.services';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './productos.html',
  styleUrl: './productos.css'
})
export class ProductosComponent implements OnInit, OnDestroy {
  currentUserRole: UserRole | null = null;
  
  // Carrito - ahora desde el servicio
  carrito: { producto: Producto, cantidad: number }[] = [];
  private carritoSubscription?: Subscription;
  mostrarCarrito: boolean = false;
  
  // Código promocional
  codigoPromo: string = '';
  promoAplicada: any = null;
  descuentoPromo: number = 0;
  validandoCodigo: boolean = false;
  mensajePromo: string = '';
  
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
    private carritoService: CarritoService,  // ← INYECTAR SERVICIO
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarCategorias();
    this.cargarProductos();
    
    // ✅ Suscribirse a cambios del carrito
    this.carritoSubscription = this.carritoService.getCarrito$().subscribe(
      carrito => {
        this.carrito = carrito;
        console.log('🛒 Carrito actualizado:', carrito);
      }
    );
  }

  ngOnDestroy() {
    // ✅ Cancelar suscripción al destruir el componente
    if (this.carritoSubscription) {
      this.carritoSubscription.unsubscribe();
    }
  }

  get esCliente(): boolean {
    return this.currentUserRole === 'Cliente';
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
    
    if (this.currentUserRole !== 'Administrador') {
      filtrados = filtrados.filter(p => p.stock > 0);
    }
    
    if (this.categoriaSeleccionada !== 'todas') {
      const categoriaId = parseInt(this.categoriaSeleccionada);
      filtrados = filtrados.filter(p => p.id_categoria === categoriaId);
    }
    
    if (this.busqueda) {
      const termino = this.busqueda.toLowerCase();
      filtrados = filtrados.filter(p => 
        p.nombre.toLowerCase().includes(termino) || 
        p.descripcion.toLowerCase().includes(termino)
      );
    }
    
    return filtrados;
  }

  isAdmin(): boolean {
    return this.currentUserRole === 'Administrador';
  }

  abrirModalCrear() {
    if (!this.isAdmin()) {
      alert('Solo el administrador puede crear productos');
      return;
    }
    this.productoEditando = {
      id_producto: 0,
      nombre: '',
      descripcion: '',
      precio: 0,
      stock: 0,
      id_categoria: this.categorias[0]?.id_categoria || 1
    };
    this.mostrarModalEditar = true;
  }

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
    
    if (this.productoEditando.id_producto > 0) {
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
          this.cargarProductos();
        },
        error: (error) => {
          console.error('Error al actualizar producto:', error);
          alert('Error al actualizar el producto');
        }
      });
    } else {
      this.http.post<Producto>(
        'http://localhost:7000/products',
        this.productoEditando,
        { headers: this.getHeaders() }
      ).subscribe({
        next: (nuevoProducto: Producto) => {
          alert('Producto creado correctamente');
          this.cerrarModalEditar();
          this.cargarProductos();
        },
        error: (error) => {
          console.error('Error al crear producto:', error);
          alert('Error al crear el producto');
        }
      });
    }
  }
    
  // ✅ CARRITO - Ahora usa el servicio
  agregarAlCarrito(producto: Producto) {
    const agregado = this.carritoService.agregarProducto(producto);
    
    if (agregado) {
      alert(`${producto.nombre} agregado al carrito`);
    } else {
      alert(`No hay más stock disponible de ${producto.nombre}`);
    }
  }

  quitarDelCarrito(productoId: number) {
    this.carritoService.quitarProducto(productoId);
  }

  cambiarCantidad(productoId: number, cambio: number) {
    const exito = this.carritoService.cambiarCantidad(productoId, cambio);
    
    if (!exito && cambio > 0) {
      const item = this.carrito.find(i => i.producto.id_producto === productoId);
      if (item) {
        alert(`No hay más stock disponible de ${item.producto.nombre}`);
      }
    }
  }

  get totalCarrito(): number {
    return this.carritoService.getTotal();
  }

  get totalConDescuento(): number {
    return this.totalCarrito - this.descuentoPromo;
  }

  get cantidadItems(): number {
    return this.carritoService.getCantidadTotal();
  }

  validarCodigo() {
    if (!this.codigoPromo.trim()) {
      this.mensajePromo = 'Ingresa un código';
      return;
    }

    this.validandoCodigo = true;
    this.mensajePromo = '';

    const productos = this.carrito.map(item => ({
      nombre: item.producto.nombre,
      cantidad: item.cantidad,
      precio: item.producto.precio
    }));

    this.http.post('http://localhost:7000/validar-codigo', {
      codigo: this.codigoPromo.toUpperCase(),
      productos: productos,
      total: this.totalCarrito
    }).subscribe({
      next: (response: any) => {
        if (response.valido) {
          this.promoAplicada = response.promocion;
          this.descuentoPromo = response.descuento;
          this.mensajePromo = `✓ ${response.mensaje}`;
        }
      },
      error: (error) => {
        this.mensajePromo = error.error?.mensaje || 'Código no válido';
        this.promoAplicada = null;
        this.descuentoPromo = 0;
      },
      complete: () => {
        this.validandoCodigo = false;
      }
    });
  }

  quitarPromo() {
    this.codigoPromo = '';
    this.promoAplicada = null;
    this.descuentoPromo = 0;
    this.mensajePromo = '';
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
      id_producto: item.producto.id_producto,
      producto: item.producto.nombre,
      cantidad: item.cantidad,
      precio: item.producto.precio
    }));

    const nuevoPedido: any = {
      id_usuario: currentUser.email,
      items: items,
      total: this.totalConDescuento,
      estado: 'Recibido',
      metodo_pago: 'Efectivo'
    };

    if (this.promoAplicada) {
      nuevoPedido.codigo_promocional = this.promoAplicada.codigo;
      nuevoPedido.descuento = this.descuentoPromo;
    }

    this.http.post('http://localhost:7000/pedidos', nuevoPedido, { headers: this.getHeaders() }).subscribe({
      next: (response) => {
        let mensaje = `¡Pedido realizado con éxito!\n\nSubtotal: $${this.totalCarrito.toLocaleString('es-AR')}`;
        
        if (this.descuentoPromo > 0) {
          mensaje += `\nDescuento (${this.promoAplicada.codigo}): -$${this.descuentoPromo.toLocaleString('es-AR')}`;
        }
        
        mensaje += `\nTotal: $${this.totalConDescuento.toLocaleString('es-AR')}\n\nPuedes retirar tu pedido cuando esté listo.`;
        
        alert(mensaje);
        
        // ✅ Vaciar carrito usando el servicio
        this.carritoService.vaciarCarrito();
        this.quitarPromo();
        this.mostrarCarrito = false;
      },
      error: (error) => {
        console.error('Error al crear pedido:', error);
        alert('Error al crear el pedido. Intenta de nuevo.');
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

  getImagenProducto(nombreProducto: string): string {
    const imagenesMap: { [key: string]: string } = {
      'Hamburguesa': 'assets/productos/rotiBurger.png',
      'Patitas de pollo': 'assets/productos/RotiPatitas.png',
      'Patitas de pollo x12': 'assets/productos/RotiPatitas.png',
      'Papas fritas': 'assets/productos/RotiPapitasFritas.png',
      'Ensalada': 'assets/productos/RotiEnsalada.png',
      'Chocotorta': 'assets/productos/Rotichoco.png',
      'Cheesecake': 'assets/productos/Roticheese.png'
    };

    if (imagenesMap[nombreProducto]) {
      return imagenesMap[nombreProducto];
    }

    const nombreLower = nombreProducto.toLowerCase();
    for (const [key, value] of Object.entries(imagenesMap)) {
      if (nombreLower.includes(key.toLowerCase()) || key.toLowerCase().includes(nombreLower)) {
        return value;
      }
    }

    return 'assets/logo/producto-default.png';
  }

  irAMiCuenta() {
    this.router.navigate(['/mi-cuenta']);
  }
}