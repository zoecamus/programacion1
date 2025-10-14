import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, UserRole } from '../../services/auth.services';

interface Producto {
  id: number;
  nombre: string;
  categoria: string;
  precio: number;
  stock: number;
  imagen: string;
  descripcion: string;
  activo: boolean;
}

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
  
  // Filtros
  busqueda: string = '';
  categoriaSeleccionada: string = 'todas';
  
  categorias = ['todas', 'RotiPrincipal', 'RotiGuarniciones', 'RotiPostres'];
  
  productos: Producto[] = [
    { id: 1, nombre: 'Patitas de pollo x12', categoria: 'RotiPrincipal', precio: 8500, stock: 50, imagen: 'assets/logo/RotiPatitas.png', descripcion: 'Deliciosas patitas de pollo cocidas y doradas', activo: true },
    { id: 2, nombre: 'Hamburguesa clásica', categoria: 'RotiPrincipal', precio: 10000, stock: 20, imagen: 'assets/logo/rotiBurger.png', descripcion: 'Hamburguesa con carne, lechuga, tomate y queso', activo: true },
    { id: 3, nombre: 'Ensalada fresca', categoria: 'RotiGuarniciones', precio: 2200, stock: 80, imagen: 'assets/logo/RotiEnsalada.png', descripcion: 'Ensalada mixta con verduras de estación', activo: true },
    { id: 4, nombre: 'Papas fritas', categoria: 'RotiGuarniciones', precio: 5000, stock: 25, imagen: 'assets/logo/RotiPapitasFritas.png', descripcion: 'Papas cortadas y fritas al momento', activo: true },
    { id: 5, nombre: 'Cheesecake', categoria: 'RotiPostres', precio: 2800, stock: 10, imagen: 'assets/logo/Roticheese.png', descripcion: 'Cheesecake cremoso con base de galletas', activo: true },
    { id: 6, nombre: 'Chocotorta', categoria: 'RotiPostres', precio: 2700, stock: 5, imagen: 'assets/logo/Rotichoco.png', descripcion: 'Clásica chocotorta argentina con dulce de leche', activo: true },
    { id: 7, nombre: 'Milanesa napolitana', categoria: 'RotiPrincipal', precio: 12000, stock: 35, imagen: 'assets/logo/RotiPatitas.png', descripcion: 'Milanesa con jamón, queso y salsa', activo: true },
    { id: 8, nombre: 'Pizza muzzarella', categoria: 'RotiPrincipal', precio: 9500, stock: 15, imagen: 'assets/logo/rotiBurger.png', descripcion: 'Pizza clásica con muzzarella de primera', activo: true },
    { id: 9, nombre: 'Empanadas x12', categoria: 'RotiPrincipal', precio: 7200, stock: 60, imagen: 'assets/logo/RotiPatitas.png', descripcion: 'Docena de empanadas de carne, pollo o verdura', activo: true },
    { id: 10, nombre: 'Puré de papa', categoria: 'RotiGuarniciones', precio: 3500, stock: 40, imagen: 'assets/logo/RotiEnsalada.png', descripcion: 'Puré cremoso de papas naturales', activo: true },
    { id: 11, nombre: 'Flan casero', categoria: 'RotiPostres', precio: 2500, stock: 8, imagen: 'assets/logo/Roticheese.png', descripcion: 'Flan casero con dulce de leche y crema', activo: true },
    { id: 12, nombre: 'Tarta de limón', categoria: 'RotiPostres', precio: 3200, stock: 12, imagen: 'assets/logo/Rotichoco.png', descripcion: 'Tarta con relleno de limón y merengue', activo: true }
  ];

  constructor(public authService: AuthService) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
  }

  get productosFiltrados(): Producto[] {
    let filtrados = this.productos.filter(p => p.activo);
    
    // Filtrar por categoría
    if (this.categoriaSeleccionada !== 'todas') {
      filtrados = filtrados.filter(p => p.categoria === this.categoriaSeleccionada);
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

  agregarAlCarrito(producto: Producto) {
    const item = this.carrito.find(i => i.producto.id === producto.id);
    if (item) {
      item.cantidad++;
    } else {
      this.carrito.push({ producto, cantidad: 1 });
    }
    alert(`${producto.nombre} agregado al carrito`);
  }

  quitarDelCarrito(productoId: number) {
    this.carrito = this.carrito.filter(i => i.producto.id !== productoId);
  }

  cambiarCantidad(productoId: number, cambio: number) {
    const item = this.carrito.find(i => i.producto.id === productoId);
    if (item) {
      item.cantidad += cambio;
      if (item.cantidad <= 0) {
        this.quitarDelCarrito(productoId);
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
    alert(`Compra finalizada! Total: $${this.totalCarrito.toLocaleString('es-AR')}`);
    this.carrito = [];
    this.mostrarCarrito = false;
  }
}