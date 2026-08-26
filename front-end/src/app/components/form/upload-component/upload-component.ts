import { Component, inject, signal } from '@angular/core';
import { Upload, PresignedPostResponse } from '../../../services/upload';

@Component({
  imports: [],
  selector: 'app-upload-component',
  styleUrl: './upload-component.css',
  templateUrl: './upload-component.html',
})
export class UploadComponent {
  private uploadService = inject(Upload);

  selectedFile = signal<File | null>(null);
  previewUrl = signal<string | null>(null);
  uploading = signal(false);
  mensagem = signal('');

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    this.selectedFile.set(file);
    this.mensagem.set('');

    // Revoga a URL anterior pra evitar vazamento de memória
    const oldUrl = this.previewUrl();
    if (oldUrl) URL.revokeObjectURL(oldUrl);

    this.previewUrl.set(URL.createObjectURL(file));
  }
  sendUpload(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.uploading.set(true);
    this.mensagem.set('');

    this.uploadService.getUploadUrl(file.name).subscribe({
      next: (presignedData: PresignedPostResponse) => {
        this.uploadService.uploadToMinio(presignedData, file).subscribe({
          next: () => {
            this.mensagem.set('Upload concluído com sucesso!');
            this.uploading.set(false);
            this.selectedFile.set(null);
          },
          error: (err) => {
            console.error('Erro no upload pro MinIO:', err);
            this.mensagem.set('Falha no upload.');
            this.uploading.set(false);
          },
        });
      },
      error: (err) => {
        console.error('Erro ao obter URL de upload:', err);
        this.mensagem.set('Falha ao gerar URL de upload.');
        this.uploading.set(false);
      },
    });
  }
}
