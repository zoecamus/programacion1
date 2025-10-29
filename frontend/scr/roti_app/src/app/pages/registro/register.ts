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

    console.log('🔍 Estado del formulario:', this.form.value);
    console.log('🔍 Formulario válido?', this.form.valid);
    console.log('🔍 Errores:', this.form.errors);

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      
      // Mostrar errores específicos
      const errors: string[] = [];
      
      if (this.form.get('nombre')?.invalid) {
        errors.push('Nombre debe tener al menos 2 caracteres');
      }
      if (this.form.get('apellido')?.invalid) {
        errors.push('Apellido debe tener al menos 2 caracteres');
      }
      if (this.form.get('email')?.invalid) {
        errors.push('Email inválido');
      }
      if (this.form.get('telefono')?.invalid) {
        errors.push('Teléfono requerido');
      }
      if (this.form.get('password')?.invalid) {
        errors.push('Contraseña debe tener al menos 6 caracteres');
      }
      if (this.form.get('password2')?.invalid) {
        errors.push('Debes repetir la contraseña');
      }
      if (this.form.errors?.['mismatch']) {
        errors.push('Las contraseñas no coinciden');
      }
      
      this.errorMsg = errors.join('. ') || 'Por favor completa todos los campos correctamente';
      console.log('❌ Errores del formulario:', errors);
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


    console.log('✅ Enviando registro:', payload);

    this.loading = true;
    this.auth.register(payload).subscribe({
      next: (response) => {
        console.log('✅ Respuesta del servidor:', response);
        this.loading = false;
        this.okMsg = '¡Cuenta creada correctamente! Redirigiendo al login...';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.loading = false;
        console.error('❌ Error en registro:', err);
        
        if (err.status === 409) {
          this.errorMsg = 'Este email ya está registrado';
        } else if (err.error?.error) {
          this.errorMsg = err.error.error;
        } else {
          this.errorMsg = 'Error de conexión. Intenta nuevamente.';
        }
      }
    });
  }
}