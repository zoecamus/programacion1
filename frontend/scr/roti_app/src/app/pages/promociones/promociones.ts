import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService, UserRole } from '../../services/auth.services';

interface Promocion {
  id?: number;
  titulo: string;
  descripcion: string;
  descuento: number;
  tipo: 'porcentaje' | 'monto' | '2x1' | 'combo';
  codigo: string;
  fechaInicio: string;
  fechaFin: string;
  activa: boolean;
  productos: string[];
}

@Component({
  selector: 'app-promociones',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './promociones.html',
  styleUrl: './promociones.css'
})
export class PromocionesComponent implements OnInit {
  currentUserRole: UserRole | null = null;
  promociones: Promocion[] = [];
  
  // Modal
  mostrarModal: boolean = false;
  promocionEditando: Promocion | null = null;
  
  // Filtros
  busqueda: string = '';
  filtroEstado: 'todas' | 'activas' | 'vencidas' = 'todas';
  
  dropdownAbierto: number | null = null;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarPromociones();
  }

  private getHeaders(): HttpHeaders {
    const user = localStorage.getItem('currentUser');
    const token = user ? JSON.parse(user).access_token : '';
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  cargarPromociones() {
    // Por ahora, cargar desde localStorage o datos de ejemplo
    const promocionesGuardadas = localStorage.getItem('promociones');
    
    if (promocionesGuardadas) {
      this.promociones = JSON.parse(promocionesGuardadas);
    } else {
      // Datos de ejemplo iniciales
      this.promociones = [
        {
          id: 1,
          titulo: '2x1 en Hamburguesas',
          descripcion: 'Llevá 2 hamburguesas y pagá solo 1',
          descuento: 50,
          tipo: 'porcentaje',
          codigo: 'BURGER2X1',
          fechaInicio: '2025-01-01',
          fechaFin: '2025-12-31',
          activa: true,
          productos: ['Hamburguesa clásica', 'Hamburguesa especial']
        },
        {
          id: 2,
          titulo: '20% OFF en Patitas',
          descripcion: 'Descuento en todas las patitas de pollo',
          descuento: 20,
          tipo: 'porcentaje',
          codigo: 'PATITAS20',
          fechaInicio: '2025-01-01',
          fechaFin: '2025-06-30',
          activa: true,
          productos: ['Patitas de pollo x12']
        }
      ];
      // Guardar en localStorage
      localStorage.setItem('promociones', JSON.stringify(this.promociones));
    }
  }

  estaVencida(fechaFin: string): boolean {
    return new Date(fechaFin) < new Date();
  }

  get promocionesFiltradas(): Promocion[] {
    let filtradas = this.promociones;
    
    // Filtro por estado
    if (this.filtroEstado === 'activas') {
      filtradas = filtradas.filter(p => p.activa && !this.estaVencida(p.fechaFin));
    } else if (this.filtroEstado === 'vencidas') {
      filtradas = filtradas.filter(p => this.estaVencida(p.fechaFin) || !p.activa);
    }
    
    // Filtro por búsqueda
    if (this.busqueda) {
      const termino = this.busqueda.toLowerCase();
      filtradas = filtradas.filter(p =>
        p.titulo.toLowerCase().includes(termino) ||
        p.descripcion.toLowerCase().includes(termino) ||
        p.codigo.toLowerCase().includes(termino)
      );
    }
    
    return filtradas;
  }

  nuevaPromocion() {
    this.promocionEditando = {
      titulo: '',
      descripcion: '',
      descuento: 0,
      tipo: 'porcentaje',
      codigo: '',
      fechaInicio: new Date().toISOString().split('T')[0],
      fechaFin: new Date().toISOString().split('T')[0],
      activa: true,
      productos: []
    };
    this.mostrarModal = true;
  }

  editarPromocion(id: number) {
    const promo = this.promociones.find(p => p.id === id);
    if (promo) {
      this.promocionEditando = { ...promo };
      this.mostrarModal = true;
    }
    this.dropdownAbierto = null;
  }

  duplicarPromocion(id: number) {
    const promo = this.promociones.find(p => p.id === id);
    if (promo) {
      this.promocionEditando = {
        ...promo,
        id: undefined,
        codigo: promo.codigo + '_COPIA',
        titulo: promo.titulo + ' (Copia)'
      };
      this.mostrarModal = true;
    }
    this.dropdownAbierto = null;
  }

  eliminarPromocion(id: number) {
    if (confirm('¿Eliminar esta promoción?')) {
      this.promociones = this.promociones.filter(p => p.id !== id);
      // Guardar en localStorage
      localStorage.setItem('promociones', JSON.stringify(this.promociones));
      alert('Promoción eliminada');
    }
    this.dropdownAbierto = null;
  }

  guardarPromocion() {
    if (!this.promocionEditando) return;
    
    if (this.promocionEditando.id) {
      // Editar
      const index = this.promociones.findIndex(p => p.id === this.promocionEditando!.id);
      if (index !== -1) {
        this.promociones[index] = { ...this.promocionEditando };
      }
      alert('Promoción actualizada');
    } else {
      // Nueva
      this.promocionEditando.id = Math.max(0, ...this.promociones.map(p => p.id || 0)) + 1;
      this.promociones.push({ ...this.promocionEditando });
      alert('Promoción creada');
    }
    
    // Guardar en localStorage
    localStorage.setItem('promociones', JSON.stringify(this.promociones));
    
    this.cerrarModal();
  }

  cerrarModal() {
    this.mostrarModal = false;
    this.promocionEditando = null;
  }

  toggleDropdown(id: number) {
    this.dropdownAbierto = this.dropdownAbierto === id ? null : id;
  }

  getTipoBadgeClass(tipo: string): string {
    switch(tipo) {
      case 'porcentaje': return 'text-bg-primary';
      case 'monto': return 'text-bg-success';
      case '2x1': return 'text-bg-warning';
      case 'combo': return 'text-bg-info';
      default: return 'text-bg-secondary';
    }
  }

  getTipoIcono(tipo: string): string {
    switch(tipo) {
      case 'porcentaje': return 'percent';
      case 'monto': return 'currency-dollar';
      case '2x1': return 'cart-plus';
      case 'combo': return 'box-seam';
      default: return 'tag';
    }
  }

  enviarPromocion() {
    alert('Funcionalidad de enviar promoción por email/SMS en desarrollo');
  }
}