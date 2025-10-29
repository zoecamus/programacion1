import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.services';

interface Pedido {
  id_pedido: number;
  id_usuario: string;
  cliente: string;
  items: { producto: string, cantidad: number, precio: number }[];
  total: number;
  estado: string;
  metodo_pago: string;
  telefono: string;
  valorado?: boolean;
}

interface Valoracion {
  id_pedido: number;
  puntaje: number;
  mensaje: string;
}

@Component({
  selector: 'app-valoracion',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './valoracion.html',
  styleUrl: './valoracion.css'
})
export class ValoracionComponent implements OnInit {
  pedidosParaValorar: Pedido[] = [];
  loading: boolean = true;
  error: string = '';
  
  // Modal de valoración
  mostrarModal: boolean = false;
  pedidoSeleccionado: Pedido | null = null;
  puntajeSeleccionado: number = 0;
  mensajeValoracion: string = '';
  enviandoValoracion: boolean = false;

  constructor(
    private authService: AuthService,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    if (!this.authService.isLoggedIn()) {
      alert('Debes iniciar sesión');
      this.router.navigate(['/login']);
      return;
    }
    
    if (this.authService.getUserRole() !== 'Cliente') {
      alert('Solo los clientes pueden valorar pedidos');
      this.router.navigate(['/']);
      return;
    }

    this.cargarPedidos();
  }

  cargarPedidos() {
    this.loading = true;
    const token = this.authService.getToken();
    const userEmail = this.authService.getEmail();
    
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    // Primero cargar las valoraciones existentes
    this.http.get<any>('http://localhost:7000/valoraciones', { headers })
      .subscribe({
        next: (valoraciones) => {
          const valoracionesUsuario = valoraciones.filter(
            (v: any) => v.id_usuario === userEmail
          );
          
          const pedidosValorados = new Set(valoracionesUsuario.map((v: any) => v.id_pedido));
          
          // Luego cargar pedidos del cliente
          this.http.get<any>(`http://localhost:7000/pedidos?id_usuario=${userEmail}`, { headers })
            .subscribe({
              next: (response) => {
                // Filtrar solo pedidos retirados que NO han sido valorados
                this.pedidosParaValorar = (response.pedidos || response).filter(
                  (p: Pedido) => p.estado === 'Retirado' && !pedidosValorados.has(p.id_pedido)
                );
                this.loading = false;
                console.log('📦 Pedidos para valorar:', this.pedidosParaValorar);
                console.log('✅ Pedidos ya valorados:', Array.from(pedidosValorados));
              },
              error: (error) => {
                console.error('❌ Error al cargar pedidos:', error);
                this.error = 'Error al cargar tus pedidos';
                this.loading = false;
              }
            });
        },
        error: (error) => {
          console.error('❌ Error al cargar valoraciones:', error);
          // Si falla, continuar sin filtrar por valoraciones
          this.http.get<any>(`http://localhost:7000/pedidos?id_usuario=${userEmail}`, { headers })
            .subscribe({
              next: (response) => {
                this.pedidosParaValorar = (response.pedidos || response).filter(
                  (p: Pedido) => p.estado === 'Retirado'
                );
                this.loading = false;
              },
              error: (error) => {
                console.error('❌ Error al cargar pedidos:', error);
                this.error = 'Error al cargar tus pedidos';
                this.loading = false;
              }
            });
        }
      });
  }

  abrirModalValoracion(pedido: Pedido) {
    this.pedidoSeleccionado = pedido;
    this.puntajeSeleccionado = 0;
    this.mensajeValoracion = '';
    this.mostrarModal = true;
  }

  cerrarModal() {
    this.mostrarModal = false;
    this.pedidoSeleccionado = null;
    this.puntajeSeleccionado = 0;
    this.mensajeValoracion = '';
  }

  seleccionarPuntaje(puntaje: number) {
    this.puntajeSeleccionado = puntaje;
  }

  enviarValoracion() {
    if (!this.pedidoSeleccionado || this.puntajeSeleccionado === 0) {
      alert('Por favor selecciona una calificación');
      return;
    }

    this.enviandoValoracion = true;
    const token = this.authService.getToken();
    
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    const valoracion = {
      id_pedido: this.pedidoSeleccionado.id_pedido,
      puntaje: this.puntajeSeleccionado,
      mensaje: this.mensajeValoracion.trim()
    };

    this.http.post('http://localhost:7000/valoraciones', valoracion, { headers })
      .subscribe({
        next: (response) => {
          console.log('✅ Valoración enviada:', response);
          alert('¡Gracias por tu valoración!');
          this.cerrarModal();
          this.cargarPedidos(); // Recargar para quitar el pedido valorado
        },
        error: (error) => {
          console.error('❌ Error al enviar valoración:', error);
          this.enviandoValoracion = false;
          
          if (error.status === 400 && error.error?.error?.includes('Ya has valorado')) {
            alert('Ya has valorado este pedido anteriormente');
            this.cerrarModal();
            this.cargarPedidos();
          } else {
            alert('Error al enviar la valoración. Intenta de nuevo.');
          }
        }
      });
  }

  volverAPedidos() {
    this.router.navigate(['/pedidos']);
  }
}