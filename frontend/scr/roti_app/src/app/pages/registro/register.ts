import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.services';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class RegisterComponent {
  form!: FormGroup;
  loading = false;
  errorMsg = '';
  okMsg = '';

  constructor(
    private fb: FormBuilder, 
    private auth: AuthService, 
    private router: Router
  ) {
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(2)]],
      apellido: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      password2: ['', [Validators.required]]
    }, { validators: this.samePassword });
  }

  // Verifica que las contraseñas sean iguales
  samePassword(group: FormGroup) {
    const a = group.get('password')?.value;
    const b = group.get('password2')?.value;
    return a && b && a !== b ? { mismatch: true } : null;
  }

  submit() {
    this.errorMsg = '';
    this.okMsg = '';

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMsg = 'Por favor completa todos los campos correctamente';
      return;
    }

    const { nombre, apellido, email, telefono, password } = this.form.value;

    // El payload debe coincidir con lo que espera el backend
    const payload = {
      id_usuario: email,  // ← El backend espera id_usuario
      nombre,
      apellido,
      email,
      telefono,
      password,
      rol: 'Cliente'  // ← Siempre Cliente para registros públicos
    };


    console.log('Enviando registro:', payload);

    this.loading = true;
    this.auth.register(payload).subscribe({
      next: (ok) => {
        this.loading = false;
        if (ok) {
          this.okMsg = '¡Cuenta creada correctamente! Redirigiendo al login...';
          setTimeout(() => this.router.navigate(['/login']), 2000);
        } else {
          this.errorMsg = 'No se pudo crear la cuenta. Revisa los datos.';
        }
      },
      error: (err) => {
        this.loading = false;
        console.error('Error en registro:', err);
        this.errorMsg = 'Error de conexión. Intenta nuevamente.';
      }
    });
  }
}