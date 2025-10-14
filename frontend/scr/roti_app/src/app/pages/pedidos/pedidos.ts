import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, UserRole } from '../../services/auth.services';

interface Pedido {
  id: number;
  fecha: Date;
  cliente: string;
  items: { producto: string, cantidad: number, precio: number }[];
  total: number;
  estado: 'Recibido' | 'En preparación' | 'En camino' | 'Entregado' | 'Cancelado';
  pagado: boolean;
  direccion: string;
  telefono: string;
  repartidor?: string;
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
  
  // Modal
  mostrarModal: boolean = false;
  pedidoDetalle: Pedido | null = null;
  
  // Filtros
  busqueda: string = '';
  filtroEstado: string = 'todos';
  
  pedidosOriginales: Pedido[] = [
    {
      id: 901,
      fecha: new Date('2024-10-12T10:30:00'),
      cliente: 'María Eva Modarelli',
      items: [
        { producto: 'Hamburguesa clásica', cantidad: 2, precio: 10000 },
        { producto: 'Papas fritas', cantidad: 1, precio: 5000 }
      ],
      total: 25000,
      estado: 'Recibido',
      pagado: false,
      direccion: 'Calle Falsa 123, Las Heras',
      telefono: '+54 261 555-1234'
    },
    {
      id: 902,
      fecha: new Date('2024-10-12T11:15:00'),
      cliente: 'Juan Pérez',
      items: [
        { producto: 'Pizza muzzarella', cantidad: 1, precio: 9500 },
        { producto: 'Cheesecake', cantidad: 2, precio: 2800 }
      ],
      total: 15100,
      estado: 'En preparación',
      pagado: true,
      direccion: 'Av. San Martín 456',
      telefono: '+54 261 555-5678',
      repartidor: 'Pedro Sánchez'
    },
    {
      id: 903,
      fecha: new Date('2024-10-12T12:00:00'),
      cliente: 'Ana García',
      items: [
        { producto: 'Empanadas x12', cantidad: 1, precio: 7200 },
        { producto: 'Ensalada fresca', cantidad: 1, precio: 2200 }
      ],
      total: 9400,
      estado: 'En camino',
      pagado: true,
      direccion: 'Las Heras Centro',
      telefono: '+54 261 555-9012',
      repartidor: 'Diego Fernández'
    },
    {
      id: 904,
      fecha: new Date('2024-10-11T19:30:00'),
      cliente: 'Carlos Rodríguez',
      items: [
        { producto: 'Milanesa napolitana', cantidad: 1, precio: 12000 }
      ],
      total: 12000,
      estado: 'Entregado',
      pagado: true,
      direccion: 'Barrio El Resguardo',
      telefono: '+54 261 555-3456'
    },
    {
      id: 905,
      fecha: new Date('2024-10-11T20:00:00'),
      cliente: 'Laura Martínez',
      items: [
        { producto: 'Patitas de pollo x12', cantidad: 2, precio: 8500 },
        { producto: 'Puré de papa', cantidad: 2, precio: 3500 }
      ],
      total: 24000,
      estado: 'Cancelado',
      pagado: false,
      direccion: 'Las Heras Norte',
      telefono: '+54 261 555-7890'
    }
  ];

  constructor(public authService: AuthService) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
  }

  get pedidos(): Pedido[] {
    let filtrados = this.pedidosOriginales;
    
    // Filtrar por estado
    if (this.filtroEstado !== 'todos') {
      filtrados = filtrados.filter(p => p.estado === this.filtroEstado);
    }
    
    // Filtrar por búsqueda
    if (this.busqueda) {
      const termino = this.busqueda.toLowerCase();
      filtrados = filtrados.filter(p => 
        p.id.toString().includes(termino) || 
        p.cliente.toLowerCase().includes(termino)
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
    if (confirm(`¿Cambiar el estado del pedido #${pedido.id} a "${nuevoEstado}"?`)) {
      pedido.estado = nuevoEstado;
      alert(`Estado actualizado a "${nuevoEstado}"`);
    }
  }

  getEstadoBadgeClass(estado: string): string {
    switch(estado) {
      case 'Recibido': return 'text-bg-secondary';
      case 'En preparación': return 'text-bg-warning';
      case 'En camino': return 'text-bg-info';
      case 'Entregado': return 'text-bg-success';
      case 'Cancelado': return 'text-bg-danger';
      default: return 'text-bg-secondary';
    }
  }

  getEstadoIcono(estado: string): string {
    switch(estado) {
      case 'Recibido': return 'inbox';
      case 'En preparación': return 'hourglass-split';
      case 'En camino': return 'truck';
      case 'Entregado': return 'check-circle';
      case 'Cancelado': return 'x-circle';
      default: return 'circle';
    }
  }

  imprimirTicket(pedido: Pedido) {
    alert(`Imprimiendo ticket del pedido #${pedido.id}`);
  }
}