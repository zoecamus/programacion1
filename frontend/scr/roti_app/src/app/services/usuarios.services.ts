import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  rol: string;
  estado: string;
  telefono: string;
  fechaRegistro: string;
}

@Injectable({
  providedIn: 'root'
})
export class UsuariosService {
  private apiUrl = 'http://localhost:7000/users'; // Cambiá el puerto si tu backend usa otro

  constructor(private http: HttpClient) {}

  getUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(this.apiUrl);
  }
}
