docker DB: docker-compose up
backend: python run.py
frotend: cd frontend -> npm run start

access DB: - docker exec -it stock_advisor_db bash
           - psql -U user -d stock_advisor
           - select * from prediction_summary
           - <SQL code>

- newsapi
- newscatcher

dark light done


accept "Apple" or "Tesla" as input
jwt auth
charts stock price
automatic stock price update
    -> OPTIONS /update_closing_prices???
    -> commit

seperate page when clicking on prediction
  - more info to prediction there