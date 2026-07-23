import { apiRequest } from './api'
export type CurrentUser={id:number;user_code:string;username:string;email:string|null;user_type:string;status:string;roles:string[];created_at:string}
export const getCurrentUser=()=>apiRequest<CurrentUser>('/api/v1/users/me')