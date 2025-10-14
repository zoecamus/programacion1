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
  
    this.authService.login(this.email, this.password).subscribe({
      next: (success) => {
        if (success) {
          // Redirigir según el rol
          const redirectUrl = this.authService.getRedirectUrl();
          console.log('Redirigiendo a:', redirectUrl);
          this.router.navigate([redirectUrl]);
        } else {
          this.mostrarError = true;
          this.mensajeError = 'Email o contraseña incorrectos';
        }
      },
      error: (error) => {
        console.error('Error en login:', error);
        this.mostrarError = true;
        this.mensajeError = 'Error al conectar con el servidor';
      }
    });
  }}