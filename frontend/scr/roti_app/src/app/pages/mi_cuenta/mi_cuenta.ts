import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.services';

interface Usuario {
  id_usuario: string;
  nombre: string;
  apellido: string;
  telefono: string;
  email: string;
  rol: string;
}

interface ValoracionConPedido {
  id_pedido: number;
  puntaje: string;
  mensaje: string;
  productos?: string[];
}

@Component({
  selector: 'app-mi_cuenta',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './mi_cuenta.html',
  styleUrl: './mi_cuenta.css'
})
export class MiCuentaComponent implements OnInit {
  // Datos del usuario
  usuario: Usuario | null = null;
  usuarioEditado: Usuario | null = null;
  
  // Valoraciones
  valoraciones: ValoracionConPedido[] = [];
  
  // Estados
  loading: boolean = true;
  error: string = '';
  modoEdicion: boolean = false;
  guardando: boolean = false;
  
  // Pestaña activa
  pestanaActiva: 'datos' | 'valoraciones' = 'datos';

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
      alert('Solo los clientes pueden acceder a esta sección');
      this.router.navigate(['/']);
      return;
    }

    this.cargarDatos();
  }

  cargarDatos() {
    this.loading = true;
    const token = this.authService.getToken();
    const userEmail = this.authService.getEmail();

    const headers = {
      'Authorization': `Bearer ${token}`
    };

    console.log('🔍 Cargando datos del usuario:', userEmail);

    // Cargar datos en paralelo usando /user (singular)
    Promise.all([
      this.http.get<any>(`http://localhost:7000/user/${userEmail}`, { headers }).toPromise(),
      this.http.get<any>('http://localhost:7000/valoraciones', { headers }).toPromise(),
      this.http.get<any>(`http://localhost:7000/pedidos?id_usuario=${userEmail}`, { headers }).toPromise()
    ]).then(([usuarioData, valoracionesData, pedidosData]) => {
      console.log('📊 Datos recibidos:', { usuarioData, valoracionesData, pedidosData });

      // Datos del usuario
      this.usuario = {
        id_usuario: usuarioData.id || usuarioData.id_usuario || usuarioData.email,
        nombre: usuarioData.nombre,
        apellido: usuarioData.apellido,
        telefono: usuarioData.telefono || '',
        email: usuarioData.email || usuarioData.id || usuarioData.id_usuario,
        rol: usuarioData.rol
      };

      // Copiar para edición
      this.usuarioEditado = { ...this.usuario };

      // Filtrar valoraciones del usuario
      const misValoraciones = valoracionesData.filter(
        (v: any) => v.id_usuario === userEmail
      );

      // Obtener información de los pedidos
      const pedidos = pedidosData.pedidos || pedidosData;

      // Enriquecer valoraciones con datos de los pedidos
      this.valoraciones = misValoraciones.map((v: any) => {
        const pedido = pedidos.find((p: any) => p.id_pedido === v.id_pedido);
        
        return {
          id_pedido: v.id_pedido,
          puntaje: v.puntaje,
          mensaje: v.mensaje || 'Sin comentarios',
          productos: pedido?.items?.map((item: any) => 
            `${item.producto} x${item.cantidad}`
          ) || []
        };
      });

      // Ordenar valoraciones
      this.valoraciones.sort((a, b) => b.id_pedido - a.id_pedido);

      this.loading = false;
      console.log('✅ Datos cargados correctamente:', { usuario: this.usuario, valoraciones: this.valoraciones });
    }).catch((error) => {
      console.error('❌ Error al cargar datos:', error);
      this.error = 'Error al cargar tus datos';
      this.loading = false;
    });
  }

  cambiarPestana(pestana: 'datos' | 'valoraciones') {
    this.pestanaActiva = pestana;
  }

  activarEdicion() {
    this.modoEdicion = true;
    this.usuarioEditado = { ...this.usuario! };
  }

  cancelarEdicion() {
    this.modoEdicion = false;
    this.usuarioEditado = { ...this.usuario! };
  }

  guardarCambios() {
    if (!this.usuarioEditado) return;

    // Validaciones
    if (!this.usuarioEditado.nombre.trim()) {
      alert('El nombre no puede estar vacío');
      return;
    }

    if (!this.usuarioEditado.apellido.trim()) {
      alert('El apellido no puede estar vacío');
      return;
    }

    this.guardando = true;
    const token = this.authService.getToken();

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    const datosActualizados = {
      nombre: this.usuarioEditado.nombre,
      apellido: this.usuarioEditado.apellido,
      telefono: this.usuarioEditado.telefono
    };

    this.http.put(
      `http://localhost:4200/user/${this.usuario!.id_usuario}`,
      datosActualizados,
      { headers }
    ).subscribe({
      next: (response) => {
        console.log('✅ Datos actualizados:', response);
        this.usuario = { ...this.usuarioEditado! };
        this.modoEdicion = false;
        this.guardando = false;
        alert('¡Datos actualizados correctamente!');
      },
      error: (error) => {
        console.error('❌ Error al actualizar:', error);
        this.guardando = false;
        alert('Error al actualizar tus datos. Intenta de nuevo.');
      }
    });
  }

  getEstrellas(puntaje: string): number[] {
    return Array(parseInt(puntaje)).fill(0);
  }

  getEstrellasVacias(puntaje: string): number[] {
    return Array(5 - parseInt(puntaje)).fill(0);
  }

  volver() {
    this.router.navigate(['/productos']);
  }

  irAValorar() {
    this.router.navigate(['/valoracion']);
  }
}