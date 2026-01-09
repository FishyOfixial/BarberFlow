// src/app/auth/jwt-interceptor.ts
import { HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from './auth';
import { switchMap, catchError, throwError } from 'rxjs';

export const JwtInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const auth = inject(AuthService);
  const token = auth.getAccessToken();

  // Clonamos request con Authorization si existe token
  const clonedReq = token ? req.clone({ headers: req.headers.set('Authorization', `Bearer ${token}`) }) : req;

  return next(clonedReq).pipe(
    catchError(err => {
      if (err.status === 401 && !req.url.endsWith('/refresh/')) {
        // Intentamos refresh
        return auth.refreshToken().pipe(
          switchMap(res => {
            const newReq = req.clone({ headers: req.headers.set('Authorization', `Bearer ${res.access}`) });
            return next(newReq);
          }),
          catchError(e => {
            auth.logout();
            return throwError(() => e);
          })
        );
      }
      return throwError(() => err);
    })
  );
};
