import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ItemCarrito {
  producto: any;
  cantidad: number;
}

@Injectable({
  providedIn: 'root'
})
export class CarritoService {
  private readonly STORAGE_KEY = 'carrito_roti';
  private carritoSubject = new BehaviorSubject<ItemCarrito[]>(this.cargarCarrito());
  
  constructor() {}

  getCarrito$(): Observable<ItemCarrito[]> {
    return this.carritoSubject.asObservable();
  }

  getCarrito(): ItemCarrito[] {
    return this.carritoSubject.value;
  }

  private cargarCarrito(): ItemCarrito[] {
    try {
      const carritoJson = localStorage.getItem(this.STORAGE_KEY);
      return carritoJson ? JSON.parse(carritoJson) : [];
    } catch (error) {
      return [];
    }
  }

  private guardarCarrito(carrito: ItemCarrito[]): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(carrito));
    this.carritoSubject.next(carrito);
  }

  agregarProducto(producto: any): boolean {
    const carrito = this.getCarrito();
    
    if (producto.stock === 0) return false;

    const itemExistente = carrito.find(
      item => item.producto.id_producto === producto.id_producto
    );

    if (itemExistente) {
      if (itemExistente.cantidad < producto.stock) {
        itemExistente.cantidad++;
        this.guardarCarrito(carrito);
        return true;
      }
      return false;
    } else {
      carrito.push({ producto, cantidad: 1 });
      this.guardarCarrito(carrito);
      return true;
    }
  }

  quitarProducto(productoId: number): void {
    const carrito = this.getCarrito().filter(
      item => item.producto.id_producto !== productoId
    );
    this.guardarCarrito(carrito);
  }

  cambiarCantidad(productoId: number, cambio: number): boolean {
    const carrito = this.getCarrito();
    const item = carrito.find(i => i.producto.id_producto === productoId);

    if (!item) return false;

    const nuevaCantidad = item.cantidad + cambio;

    if (nuevaCantidad <= 0) {
      this.quitarProducto(productoId);
      return true;
    }

    if (nuevaCantidad <= item.producto.stock) {
      item.cantidad = nuevaCantidad;
      this.guardarCarrito(carrito);
      return true;
    }

    return false;
  }

  vaciarCarrito(): void {
    this.guardarCarrito([]);
  }

  getCantidadTotal(): number {
    return this.getCarrito().reduce((total, item) => total + item.cantidad, 0);
  }

  getTotal(): number {
    return this.getCarrito().reduce(
      (total, item) => total + (item.producto.precio * item.cantidad),
      0
    );
  }
}
