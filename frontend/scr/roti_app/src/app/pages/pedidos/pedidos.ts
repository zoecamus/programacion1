import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService, UserRole } from '../../services/auth.services';


interface Pedido {
  id_pedido: number;
  id_usuario: string;
  cliente: string;
  items: { producto: string, cantidad: number, precio: number }[];
  total: number;
  estado: 'Recibido' | 'En preparación' | 'Listo para retirar' | 'Retirado';
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
    private http: HttpClient,
    private router: Router
  ) {}



  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    // Verificar si está logueado
    if (!this.authService.isLoggedIn()) {
      alert('Debes iniciar sesión para ver tus pedidos');
      this.router.navigate(['/login']);
      return;
    }
    this.cargarPedidos();
  }



  cargarPedidos() {
    this.loading = true;
    const token = this.authService.getToken();
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    let url = 'http://localhost:7000/pedidos';
    

    // ✅ Si es CLIENTE, filtrar solo SUS pedidos
    if (this.currentUserRole === 'Cliente') {
      const userEmail = this.authService.getEmail();
      url = `http://localhost:7000/pedidos?id_usuario=${userEmail}`;
      console.log('🔍 Cargando pedidos del cliente:', userEmail);
    } else {
      console.log('🔍 Cargando TODOS los pedidos (Admin/Encargado)');
    }

    this.http.get<any>(url, { headers }).subscribe({
      next: (response) => {
        console.log('✅ Pedidos cargados:', response);
        this.pedidosOriginales = response.pedidos || response;
        this.loading = false;
      },
      error: (error) => {

        console.error('❌ Error al cargar pedidos:', error);

        if (error.status === 422) {
          this.error = 'Error al cargar pedidos. Verifica que el backend esté configurado correctamente.';
        } else if (error.status === 401) {
          this.error = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
          setTimeout(() => this.router.navigate(['/login']), 2000);
        } else {
          this.error = 'Error al cargar los pedidos';
        }
        this.loading = false;
      }
    });
  }

  // Getter para mostrar si es vista de cliente
  get esCliente(): boolean {
    return this.currentUserRole === 'Cliente';
  }

  // Getter para mostrar si puede gestionar pedidos
  get puedeGestionar(): boolean {
    return this.currentUserRole === 'Administrador' || this.currentUserRole === 'Encargado';
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
    if (!this.puedeGestionar) {
      alert('No tienes permisos para cambiar el estado de pedidos');
      return;
    }
    if (confirm(`¿Cambiar el estado del pedido #${pedido.id_pedido} a "${nuevoEstado}"?`)) {
      const token = this.authService.getToken();


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
      case 'Recibido': return 'text-bg-secondary';
      case 'En preparación': return 'text-bg-warning';
      case 'Listo para retirar': return 'text-bg-info';
      case 'Retirado': return 'text-bg-success';
      default: return 'text-bg-secondary';
    }
  }

  getEstadoIcono(estado: string): string {
    switch(estado) {
      case 'Recibido': return 'inbox';
      case 'En preparación': return 'hourglass-split';
      case 'Listo para retirar': return 'bell';
      case 'Retirado': return 'check-circle';
      default: return 'circle';
    }
  }

  imprimirTicket(pedido: Pedido) {
    alert(`Imprimiendo ticket del pedido #${pedido.id_pedido}`);
  }

  volverAlMenu() {
    this.router.navigate(['/productos']);
  }

  irAValorar() {
    this.router.navigate(['/valoracion']);
  }

  irAMiCuenta() {
    this.router.navigate(['/mi-cuenta']);
  }

  volverDashboard() {
    const redirectUrl = this.authService.getRedirectUrl();
    this.router.navigate([redirectUrl]);
  }

  logout() {
    if (confirm('¿Cerrar sesión?')) {
      this.authService.logout();
    }
  }
}