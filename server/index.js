import snowflake from 'snowflake-sdk';

const connection = snowflake.createConnection({
  account: process.env.SNOWFLAKE_ACCOUNT,
  username: process.env.SNOWFLAKE_USER,
  password: process.env.SNOWFLAKE_PASSWORD,
  warehouse: 'COMPUTE_WH',
  database: 'USERSHAMZAFTEAM47',
  schema: 'PUBLIC'
});

connection.connect();

export function logGameRun(run) {
  const sql = `
    INSERT INTO runs VALUES (
      '${run.id}',
      'game',
      '${run.player}',
      '${run.mode}',
      ${run.score},
      ${run.time},
      ${run.accuracy},
      CURRENT_TIMESTAMP
    )
  `;

  connection.execute({ sqlText: sql });
}
