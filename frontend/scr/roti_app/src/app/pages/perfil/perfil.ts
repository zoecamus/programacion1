import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, User } from '../../services/auth.services';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './perfil.html',
  styleUrl: './perfil.css'
})
export class PerfilComponent implements OnInit {
  currentUser: User | null = null;
  editando: boolean = false;

  // Datos del perfil
  perfil = {
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
    ciudad: 'Las Heras, Mendoza',
    codigoPostal: '5539'
  };

  // Datos para cambiar contraseña
  cambioPassword = {
    actual: '',
    nueva: '',
    confirmar: ''
  };

  mostrarCambioPassword: boolean = false;

  constructor(public authService: AuthService) {}

  ngOnInit() {
    this.currentUser = this.authService.getCurrentUser();
    if (this.currentUser) {
      this.perfil.nombre = this.currentUser.nombre;
      this.perfil.email = this.currentUser.email;
      // En producción estos datos vendrían del backend
      this.perfil.telefono = '+54 261 555-1234';
      this.perfil.direccion = 'Calle Falsa 123';
    }
  }

  toggleEditar() {
    this.editando = !this.editando;
  }

  guardarCambios() {
    if (!this.perfil.nombre || !this.perfil.email) {
      alert('Nombre y email son obligatorios');
      return;
    }
    
    // Aquí irían las llamadas al backend
    alert('Perfil actualizado correctamente');
    this.editando = false;
  }

  cancelarEdicion() {
    // Restaurar datos originales
    if (this.currentUser) {
      this.perfil.nombre = this.currentUser.nombre;
      this.perfil.email = this.currentUser.email;
    }
    this.editando = false;
  }

  cambiarPassword() {
    if (!this.cambioPassword.actual || !this.cambioPassword.nueva || !this.cambioPassword.confirmar) {
      alert('Completa todos los campos');
      return;
    }

    if (this.cambioPassword.nueva !== this.cambioPassword.confirmar) {
      alert('Las contraseñas no coinciden');
      return;
    }

    if (this.cambioPassword.nueva.length < 6) {
      alert('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    // Aquí iría la llamada al backend
    alert('Contraseña cambiada correctamente');
    this.cambioPassword = { actual: '', nueva: '', confirmar: '' };
    this.mostrarCambioPassword = false;
  }

  eliminarCuenta() {
    if (confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
      if (confirm('¿Estás REALMENTE seguro? Se perderán todos tus datos.')) {
        alert('Cuenta eliminada');
        this.authService.logout();
      }
    }
  }}