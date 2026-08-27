import { inject, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PresignedPostResponse {
  url: string;
  fields: { [key: string]: string }
}

export interface Photo {
  key: string;
  url: string;
  last_modified: string;
}

export interface PhotosResponse {
  photos: Photo[];
}

@Service()
export class Upload {
  private http = inject(HttpClient)
  private apiUrl = 'http://localhost:8000';

  getUploadUrl(filename: string): Observable<PresignedPostResponse>{
    return this.http.post<PresignedPostResponse>(`${this.apiUrl}/upload-url`, { filename });
  }

  uploadToMinio(presignedData: PresignedPostResponse, file: File): Observable<any> {
    const formData = new FormData();

    Object.entries(presignedData.fields).forEach(([key, value]) => {
      formData.append(key, value);
    });
    formData.append('file', file);

    return this.http.post(presignedData.url, formData);
  }

  getPhotos(): Observable<PhotosResponse> {
    return this.http.get<PhotosResponse>(`${this.apiUrl}/photos`);
  }

}
