import { Routes } from '@angular/router';
import { Admin } from './pages/admin/admin';
import { Empleado } from './pages/empleado/empleado';
import { Usuario } from './pages/usuario/usuario';
export const routes: Routes = [
  { path: 'admin', component: Admin },
  { path: 'empleado', component: Empleado },
  { path: 'usuario', component: Usuario },
  { path: '', redirectTo: '/usuario', pathMatch: 'full' }, 
  { path: '**', redirectTo: '/usuario' } 
];