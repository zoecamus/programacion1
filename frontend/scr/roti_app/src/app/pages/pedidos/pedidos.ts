import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService, UserRole } from '../../services/auth.services';

interface Pedido {
  id_pedido: number;
  id_usuario: string;
  cliente: string;
  items: { producto: string, cantidad: number, precio: number }[];
  total: number;
  estado: 'Pendiente' | 'En preparación' | 'Listo para retiro' | 'Entregado';
  metodo_pago: string;
  telefono: string;
  pagado?: boolean;
}

@Component({
  selector: 'app-pedidos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pedidos.html',
  styleUrl: './pedidos.css'
})
export class PedidosComponent implements OnInit {
  currentUserRole: UserRole | null = null;
  
  mostrarModal: boolean = false;
  pedidoDetalle: Pedido | null = null;
  
  busqueda: string = '';
  filtroEstado: string = 'todos';
  
  pedidosOriginales: Pedido[] = [];
  loading: boolean = true;
  error: string = '';

  constructor(
    public authService: AuthService,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarPedidos();
  }

  cargarPedidos() {
    this.loading = true;
    const user = localStorage.getItem('currentUser');
    const token = user ? JSON.parse(user).access_token : '';
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    this.http.get<any>('http://localhost:7000/pedidos', { headers }).subscribe({
      next: (response) => {
        console.log('Pedidos cargados:', response);
        this.pedidosOriginales = response.pedidos || response;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar pedidos:', error);
        this.error = 'Error al cargar los pedidos';
        this.loading = false;
      }
    });
  }

  get pedidos(): Pedido[] {
    let filtrados = this.pedidosOriginales;
    
    if (this.filtroEstado !== 'todos') {
      filtrados = filtrados.filter(p => p.estado === this.filtroEstado);
    }
    
    if (this.busqueda) {
      const termino = this.busqueda.toLowerCase();
      filtrados = filtrados.filter(p => 
        p.id_pedido?.toString().includes(termino) || 
        p.cliente?.toLowerCase().includes(termino)
      );
    }
    
    return filtrados;
  }

  verDetalle(pedido: Pedido) {
    this.pedidoDetalle = pedido;
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
    this.pedidoDetalle = null;
  }

  cambiarEstado(pedido: Pedido, nuevoEstado: Pedido['estado']) {
    if (confirm(`¿Cambiar el estado del pedido #${pedido.id_pedido} a "${nuevoEstado}"?`)) {
      const user = localStorage.getItem('currentUser');
      const token = user ? JSON.parse(user).access_token : '';
      
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      this.http.put(
        `http://localhost:7000/pedido/${pedido.id_pedido}`,
        { estado: nuevoEstado },
        { headers }
      ).subscribe({
        next: () => {
          pedido.estado = nuevoEstado;
          if (this.pedidoDetalle?.id_pedido === pedido.id_pedido) {
            this.pedidoDetalle.estado = nuevoEstado;
          }
          alert(`Estado actualizado a "${nuevoEstado}"`);
        },
        error: (error) => {
          console.error('Error al actualizar estado:', error);
          alert('Error al actualizar el estado del pedido');
        }
      });
    }
  }

  getEstadoBadgeClass(estado: string): string {
    switch(estado) {
      case 'Pendiente': return 'text-bg-secondary';
      case 'En preparación': return 'text-bg-warning';
      case 'Listo para retiro': return 'text-bg-info';
      case 'Entregado': return 'text-bg-success';
      default: return 'text-bg-secondary';
    }
  }

  getEstadoIcono(estado: string): string {
    switch(estado) {
      case 'Pendiente': return 'inbox';
      case 'En preparación': return 'hourglass-split';
      case 'Listo para retiro': return 'bell';
      case 'Entregado': return 'check-circle';
      default: return 'circle';
    }
  }

  imprimirTicket(pedido: Pedido) {
    alert(`Imprimiendo ticket del pedido #${pedido.id_pedido}`);
  }
}