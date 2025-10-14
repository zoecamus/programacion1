import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.services';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  mostrarError: boolean = false;
  mensajeError: string = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  iniciarSesion() {
    this.mostrarError = false;

    if (!this.email || !this.password) {
      this.mostrarError = true;
      this.mensajeError = 'Por favor completa todos los campos';
      return;
    }

    if (this.authService.login(this.email, this.password)) {
      // Redirigir según el rol del usuario
      this.router.navigate([this.authService.getRedirectUrl()]);
    } else {
      this.mostrarError = true;
      this.mensajeError = 'Email o contraseña incorrectos';
    }
  }
}