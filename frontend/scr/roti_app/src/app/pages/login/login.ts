import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.services';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {
  email = '';
  password = '';
  mostrarError = false;
  mensajeError = '';

  constructor(private auth: AuthService, private router: Router) {}

  iniciarSesion() {
    this.mostrarError = false;
    this.mensajeError = '';
  
    if (!this.email || !this.password) {
      this.mostrarError = true;
      this.mensajeError = 'Completá email y contraseña.';
      return;
    }
  
    console.log('🔵 Iniciando sesión...');
    
    this.auth.login(this.email, this.password).subscribe({
      next: (ok: boolean) => {
        console.log('✅ Respuesta recibida:', ok);
        
        if (ok) {
          const dest = this.auth.getRedirectUrl();
          console.log('🚀 Redirigiendo a:', dest);
          
          this.router.navigate([dest]).then(
            (success) => console.log('✅ Navegación exitosa:', success),
            (error) => console.error('❌ Error en navegación:', error)
          );
        } else {
          console.log('❌ Login falló');
          this.mostrarError = true;
          this.mensajeError = 'Credenciales inválidas.';
        }
      },
      error: (error) => {
        console.error('❌ Error en login:', error);
        this.mostrarError = true;
        this.mensajeError = 'Error al conectar con el servidor.';
      }
    });
  }

  irARegistro() {
    console.log('🔵 Navegando a registro...');
    this.router.navigate(['/register']);
  }
}