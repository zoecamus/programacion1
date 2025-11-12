import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.services';
import { HttpClient } from '@angular/common/http';

interface Producto {
  id_producto: number;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  total_pedidos?: number;
}

interface Promocion {
  id_promocion: number;
  codigo: string;
  descripcion: string;
  tipo_descuento: string;
  valor_descuento: number;
  fecha_inicio: string;
  fecha_fin: string;
  activa: boolean;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrls: ['./home.css']
})
export class HomeComponent implements OnInit {
  
  // ✅ PRODUCTOS MÁS PEDIDOS
  productosMasPedidos: Producto[] = [];
  loadingMasPedidos = true;

  // ✅ PRODUCTOS MEJOR VALORADOS
  productosMejorValorados: Producto[] = [];
  loadingMejorValorados = true;

  promociones: Promocion[] = [];
  error = '';

  constructor(
    private router: Router,
    private authService: AuthService,
    private http: HttpClient
  ) {
    // ✅ COMENTADO: No redirigir automáticamente
    /*
    if (this.authService.isLoggedIn()) {
      console.log('👤 Usuario ya logueado, redirigiendo...');
      const redirectUrl = this.authService.getRedirectUrl();
      this.router.navigate([redirectUrl]);
    }
    */
  }

  ngOnInit() {
    this.cargarProductosMasPedidos();
    this.cargarProductosMejorValorados();
    // this.cargarPromociones(); // Descomentar si quieres promociones
  }

  /**
   * ✅ CARGAR PRODUCTOS MÁS PEDIDOS DEL BACKEND
   */
  cargarProductosMasPedidos() {
    this.loadingMasPedidos = true;
    
    // ✅ Llamar al backend con filtro mas_vendidos=true
    this.http.get<any>('http://localhost:7000/products?mas_vendidos=true&per_page=4').subscribe({
      next: (response) => {
        this.productosMasPedidos = response.productos || response;
        this.loadingMasPedidos = false;
        console.log('🔥 Productos más pedidos:', this.productosMasPedidos);
      },
      error: (error) => {
        console.error('❌ Error al cargar productos más pedidos:', error);
        this.loadingMasPedidos = false;
      }
    });
  }

  /**
   * ✅ CARGAR PRODUCTOS MEJOR VALORADOS DEL BACKEND
   */
  cargarProductosMejorValorados() {
    this.loadingMejorValorados = true;
    
    // ✅ Llamar al backend con filtro mejor_valorados=true
    this.http.get<any>('http://localhost:7000/products?mejor_valorados=true&per_page=4').subscribe({
      next: (response) => {
        this.productosMejorValorados = response.productos || response;
        this.loadingMejorValorados = false;
        console.log('⭐ Productos mejor valorados:', this.productosMejorValorados);
      },
      error: (error) => {
        console.error('❌ Error al cargar productos mejor valorados:', error);
        this.loadingMejorValorados = false;
      }
    });
  }

  cargarPromociones() {
    // Obtener promociones activas del backend
    this.http.get<any>('http://localhost:7000/promociones').subscribe({
      next: (response) => {
        // Filtrar solo promociones activas
        const todasPromociones = response.promociones || response;
        this.promociones = todasPromociones
          .filter((p: Promocion) => p.activa)
          .slice(0, 3); // Mostrar máximo 3
        
        console.log('✅ Promociones cargadas:', this.promociones);
      },
      error: (error) => {
        console.error('❌ Error al cargar promociones:', error);
      }
    });
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

    // Buscar coincidencia exacta primero
    if (imagenesMap[nombreProducto]) {
      return imagenesMap[nombreProducto];
    }

    // Buscar coincidencia parcial (case insensitive)
    const nombreLower = nombreProducto.toLowerCase();
    for (const [key, value] of Object.entries(imagenesMap)) {
      if (nombreLower.includes(key.toLowerCase()) || key.toLowerCase().includes(nombreLower)) {
        return value;
      }
    }

    // Imagen por defecto
    return 'assets/logo/producto-default.png';
  }

  verMenu() {
    console.log('🔵 Redirigiendo a login para autenticación');
    this.router.navigate(['/login']);
  }

  irALogin() {
    console.log('🔵 Navegando a login');
    this.router.navigate(['/login']);
  }

  scrollTo(elementId: string) {
    const element = document.getElementById(elementId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  getTipoDescuentoTexto(promo: Promocion): string {
    if (promo.tipo_descuento === 'porcentaje') {
      return `${promo.valor_descuento}% OFF`;
    } else {
      return `-$${promo.valor_descuento.toLocaleString('es-AR')}`;
    }
  }
}