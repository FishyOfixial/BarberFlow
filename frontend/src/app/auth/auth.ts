// src/app/auth/auth.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap, switchMap } from 'rxjs/operators';
import * as jwt_decode from 'jwt-decode';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://127.0.0.1:8000/api/auth';
  private tokenRefreshing = false;
  private refreshSubject = new BehaviorSubject<string | null>(null);

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login/`, { username, password }).pipe(
      tap(res => {
        this.saveAccessToken(res.access);
        this.saveRefreshToken(res.refresh);
        this.saveRoleFromToken(res.access);
      }),
      catchError(err => throwError(err))
    );
  }

  refreshToken(): Observable<any> {
    const refresh = this.getRefreshToken();
    if (!refresh) return throwError('No refresh token');

    return this.http.post<any>(`${this.apiUrl}/refresh/`, { refresh }).pipe(
      tap(res => {
        this.saveAccessToken(res.access);
        this.saveRoleFromToken(res.access);
      }),
      catchError(err => throwError(err))
    );
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh');
  }

  saveAccessToken(token: string) {
    localStorage.setItem('access', token);
  }

  saveRefreshToken(token: string) {
    localStorage.setItem('refresh', token);
  }

  saveRole(role: string) {
    localStorage.setItem('role', role);
  }

  saveRoleFromToken(token: string){
    try {
        const decoded: any = jwt_decode.jwtDecode(token);
        if (decoded.role) {
          this.saveRole(decoded.role)
        }
    } catch (e) {
      console.warn('No se pudo identificar el JWT para extraer el role');
    }
  }

  getRole(): string | null {
    return localStorage.getItem('role');
  }

  logout() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('role');
  }
}
