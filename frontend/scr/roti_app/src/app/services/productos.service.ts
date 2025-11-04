import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Producto {
  id_producto: number;
  nombre: string;
  precio: number;
  stock: number;
  descripcion: string;
  id_categoria: number;
}

export interface Categoria {
  id_categoria: number;
  nombre: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProductosService {
  private apiUrl = 'http://localhost:7000/products';
  private categoriasUrl = 'http://localhost:7000/categorias';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const user = localStorage.getItem('currentUser');
    const token = user ? JSON.parse(user).access_token : '';
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  getProductos(params?: any): Observable<any> {
    let url = this.apiUrl;
    if (params) {
      const queryParams = new URLSearchParams(params).toString();
      url += `?${queryParams}`;
    }
    return this.http.get<any>(url);
  }

  getProducto(id: number): Observable<Producto> {
    return this.http.get<Producto>(`http://localhost:7000/product/${id}`);
  }

  getCategorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(this.categoriasUrl);
  }

  crearProducto(producto: Producto): Observable<Producto> {
    return this.http.post<Producto>(this.apiUrl, producto, { headers: this.getHeaders() });
  }

  actualizarProducto(id: number, producto: Producto): Observable<Producto> {
    return this.http.put<Producto>(`http://localhost:7000/product/${id}`, producto, { headers: this.getHeaders() });
  }

  eliminarProducto(id: number): Observable<any> {
    return this.http.delete(`http://localhost:7000/product/${id}`, { headers: this.getHeaders() });
  }
}