import { apiRequest } from './api'

export interface UserFoodPreferences {
  exclude_ingredients: string[]
  preferred_ingredients: string[]
}

export const getUserFoodPreferences = () =>
  apiRequest<UserFoodPreferences>('/api/v1/users/preferences')

export const saveUserFoodPreferences = (preferences: UserFoodPreferences) =>
  apiRequest<UserFoodPreferences>('/api/v1/users/preferences', {
    method: 'PUT',
    body: JSON.stringify(preferences),
  })