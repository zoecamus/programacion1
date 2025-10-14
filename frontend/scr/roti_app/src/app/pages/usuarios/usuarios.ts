import { Component, OnInit } from '@angular/core';
import { UsuariosService, Usuario } from '../../services/usuarios.services';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-usuarios',
  standalone: true,
  templateUrl: './usuarios.html',
  styleUrls: ['./usuarios.css'],
  imports: [CommonModule, FormsModule, HttpClientModule]
})
export class UsuariosComponent implements OnInit {
  usuarios: Usuario[] = []; 
  busqueda: string = '';

  constructor(private usuarioService: UsuariosService) {}

  ngOnInit() {
      this.usuarioService.getUsuarios().subscribe({
        next: (data) => {
          // Convertir 'encargado' en 'empleado'
          this.usuarios = data.map(u => ({
            ...u,
            rol: u.rol === 'encargado' ? 'empleado' : u.rol
          }));
        },
        error: (err) => console.error('Error al obtener usuarios:', err)
      });
    }
    
  // Getter que aplica el filtro de búsqueda
  
  get usuariosFiltrados(): Usuario[] {
    const termino = this.busqueda.toLowerCase();
    return this.usuarios.filter(u =>
      u.nombre.toLowerCase().includes(termino) ||
      u.email.toLowerCase().includes(termino) ||
      u.rol.toLowerCase().includes(termino)
    )}
   
  getRolBadgeClass(rol: string): string {
      switch(rol) {
        case 'admin': return 'text-bg-danger';
        case 'repartidor': return 'text-bg-info';
        case 'cliente': return 'text-bg-primary';
        default: return 'text-bg-secondary';
      }
    }
    
  getRolTexto(rol: string): string {
      switch(rol) {
        case 'admin': return '👨‍💼 Admin';
        case 'empleado': return '🚴 empleado';
        case 'cliente': return '🛒 Cliente';
        default: return rol;
      }
    }
    
    editarUsuario(id: number) {
      alert(`Función editarUsuario aún no implementada. ID: ${id}`);
      // Podés abrir un modal, redireccionar o lo que necesites.
    }
    eliminarUsuario(id: number) {
      if (confirm('¿Estás seguro de eliminar este usuario?')) {
        this.usuarios = this.usuarios.filter(u => u.id !== id);
      }
    }
    
    
  }

