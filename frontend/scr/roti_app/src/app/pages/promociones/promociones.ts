import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService, UserRole } from '../../services/auth.services';
import { Router } from '@angular/router';

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
  
  mostrarModal: boolean = false;
  promocionEditando: Promocion | null = null;
  
  busqueda: string = '';
  filtroEstado: 'todas' | 'activas' | 'vencidas' = 'todas';
  
  dropdownAbierto: number | null = null;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarPromociones();
  }

  
  volverDashboard() {
  const redirectUrl = this.authService.getRedirectUrl();
  this.router.navigate([redirectUrl]);
  }
  
  
  cargarPromociones() {
    this.http.get<any>('http://localhost:7000/promociones').subscribe({
      next: (response) => {
        console.log('Promociones cargadas:', response);
        this.promociones = response.promociones || [];
      },
      error: (err) => {
        console.error('Error al cargar promociones:', err);
      }
    });
  }

  estaVencida(fechaFin: string): boolean {
    return new Date(fechaFin) < new Date();
  }

  get promocionesFiltradas(): Promocion[] {
    let filtradas = this.promociones;
    
    if (this.filtroEstado === 'activas') {
      filtradas = filtradas.filter(p => p.activa && !this.estaVencida(p.fechaFin));
    } else if (this.filtroEstado === 'vencidas') {
      filtradas = filtradas.filter(p => this.estaVencida(p.fechaFin) || !p.activa);
    }
    
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
      const token = this.authService.getToken();
      const headers = new HttpHeaders({ 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      });

      this.http.delete(`http://localhost:7000/promocion/${id}`, { headers }).subscribe({
        next: () => {
          alert('Promoción eliminada');
          this.cargarPromociones();
        },
        error: (err) => {
          console.error('Error al eliminar:', err);
          alert('Error al eliminar promoción');
        }
      });
    }
    this.dropdownAbierto = null;
  }
  guardando: boolean = false;

  guardarPromocion() {
    if (!this.promocionEditando || this.guardando) return;  // ← Evita doble submit
  
    this.guardando = true;  // ← Deshabilita el botón
  
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  
    if (this.promocionEditando.id) {
      // Editar
      this.http.put(
        `http://localhost:7000/promocion/${this.promocionEditando.id}`,
        this.promocionEditando,
        { headers }
      ).subscribe({
        next: () => {
          alert('Promoción actualizada');
          this.cargarPromociones();
          this.cerrarModal();
          this.guardando = false;  // ← Rehabilita
        },
        error: (err) => {
          console.error('Error al actualizar:', err);
          alert('Error al actualizar promoción');
          this.guardando = false;  // ← Rehabilita
        }
      });
    } else {
      // Crear nueva
      this.http.post('http://localhost:7000/promociones', this.promocionEditando, { headers }).subscribe({
        next: () => {
          alert('Promoción creada');
          this.cargarPromociones();
          this.cerrarModal();
          this.guardando = false;  // ← Rehabilita
        },
        error: (err) => {
          console.error('Error al crear:', err);
          alert('Error al crear promoción');
          this.guardando = false;  // ← Rehabilita
        }
      });
    }
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

  puedeEditar(): boolean {
    return this.currentUserRole === 'Encargado' || this.currentUserRole === 'Administrador';
  }

  esAdmin(): boolean {
    return this.currentUserRole === 'Administrador';
  }

  copiarCodigo(codigo: string) {
    navigator.clipboard.writeText(codigo).then(() => {
      alert(`Código ${codigo} copiado al portapapeles`);
    }).catch(() => {
      alert('No se pudo copiar el código');
    });
  }

  enviarPromocion() {
    alert('Funcionalidad de enviar promoción por email/SMS en desarrollo');
  }
}